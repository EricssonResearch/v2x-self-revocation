import asyncio
import asyncio_dgram
import logging
import aiohttp
import gc
import signal

import conf
import utils
import log
from attacker import Attacker
from broadcast import Broadcast
from credentials import CredentialManager

group = utils.get_random_int(1, conf.env("NUM_GROUPS"))
broadcast_heartbeat = Broadcast(conf.env("HEARTBEAT_PORT"))
broadcast_v2v = Broadcast(conf.env("V2V_PORT") + group, random_group=False)
broadcast_log = Broadcast(conf.env("LOG_PORT") + group, random_group=False)
cred_manager = CredentialManager()
q = asyncio.Queue()

async def exit_checker():
    await q.get()
    logging.debug("TC is revoked.")


async def movement_manager():
    global group
    random_movement = conf.env("RANDOM_MOVEMENT")
    num_groups = conf.env("NUM_GROUPS")

    try:
        while True:
            try:
                wait_time = utils.get_random_int(1, conf.env("MOVEMENT_PERIOD"))
                await asyncio.sleep(wait_time)

                if random_movement:
                    group = utils.get_random_int(1, num_groups)
                else:
                    group = 1 if group >= num_groups else group + 1

                logging.debug(f"Moving to group {group}")
                broadcast_v2v.close()
                broadcast_log.close()
                await broadcast_v2v.update_port(conf.env("V2V_PORT") + group)
                await broadcast_log.update_port(conf.env("LOG_PORT") + group)
            except Exception as e:
                logging.error(f"movement_manager: {e}")
    except asyncio.CancelledError:
        pass

async def heartbeat_receiver(tc_session):
    try:
        atk = Attacker(conf.env("ATTACKER_LEVEL"), tc_session, cred_manager, q)

        while True:
            try:
                data = await broadcast_heartbeat.recv()
                await atk.process_heartbeat(data)
            except Exception as e:
                logging.error(f"heartbeat_receiver: {e}")

    except asyncio.CancelledError:
        pass

async def v2v_receiver(tc_session):
    try:
        while True:
            try:
                data = await broadcast_v2v.recv()
                decoded_data = utils.decode_jwt(data)
                ps = decoded_data["payload"]["iss"]
                malicious = decoded_data["payload"]["malicious"]

                if ps in cred_manager.get_pseudonyms():
                    # this is our own message, skip
                    continue

                async with tc_session.post("/verify", data=data) as response:
                    # check if TC is still operational
                    if response.status == 403:
                        q.put_nowait(True)
                    # log if request has failed
                    if response.status != 200:
                        logging.debug(
                            f"TC/verify failed: {response.status} {await response.text()}".strip()
                        )
                    # log to UDP otherwise
                    else:
                        if malicious and conf.env("LOG_TO_UDP"):
                            own_ps = ' '.join(cred_manager.get_pseudonyms())
                            await broadcast_log.send(f"VERIFY {ps} {own_ps}".encode())
            except asyncio_dgram.aio.TransportClosed:
                # we are changing group, wait until the new is initialized
                await asyncio.sleep(0.1)
            except Exception as e:
                logging.error(f"v2v_receiver: {e.__class__} {e}")

    except asyncio.CancelledError:
        pass


async def message_generator(tc_session):
    try:
        v2v_period = conf.env("V2V_GENERATION_PERIOD")
        malicious = conf.env("VEHICLE_MALICIOUS")

        while True:
            await asyncio.sleep(v2v_period)
            ps = cred_manager.get_random_pseudonym()
            if ps is None:
                continue # cannot use any pseudonyms

            #logging.debug("Generating a new V2V message")
            msg = {
                "iss": ps,
                "malicious": malicious,
                # TODO fields here are optional and depend on the data to send
                "data": utils.generate_random_string(64)
            }

            # sending to TC for signature
            try:
                async with tc_session.post("/sign", json=msg) as response:
                    # remove pseudonym if unusable
                    if response.status == 401:
                        cred_manager.remove_pseudonym(ps)
                    # check if TC is still operational
                    elif response.status == 403:
                        q.put_nowait(True)
                    # log if request has failed
                    if response.status != 200:
                        logging.debug(f"TC/sign failed: {response.status} {await response.text()}".strip())
                    # log to UDP otherwise
                    else:
                        signed_msg = await response.read()
                        #logging.debug(f"Message signed: {signed_msg}")
                        await broadcast_v2v.send(signed_msg)
                        if conf.env("LOG_TO_UDP"):
                            await broadcast_log.send(f"SIGN {ps} {int(malicious)}".encode())
            except Exception as e:
                logging.error(f"message_generator: {e}")
    except asyncio.CancelledError:
        pass


async def pseudonym_refresher(tc_session):
    try:
        num_pseudonyms = conf.env("NUM_PSEUDONYMS")
        while True:
            for _ in range(num_pseudonyms):
                try:
                    async with tc_session.get("/create") as response:
                        # check if TC is still operational
                        if response.status == 403:
                            q.put_nowait(True)
                        # log if request has failed
                        if response.status != 200:
                            logging.debug(f"TC/create failed: {response.status} {await response.text()}".strip())
                        # add new pseudonym to list otherwise
                        else:
                            ps = await response.text()
                            #logging.debug(f"New pseudonym: {ps}")
                            cred_manager.add_pseudonym(ps)
                except Exception as e:
                    logging.error(f"pseudonym_refresher: {e}")

            await asyncio.sleep(conf.env("PSEUDONYM_REFRESH_PERIOD"))
    except asyncio.CancelledError:
        pass


async def join(tc_session):
    # get TC's public key
    async with tc_session.get("/pubkey") as response:
        if response.status != 200:
            raise Exception(
                f"Failed to get TC's pubkey: {response.status} {await response.text()}"
            )

        pubkey = await response.text()

    #logging.debug(f"TC's key: {pubkey}")

    # get data from issuer and send to TC
    async with aiohttp.ClientSession("http://issuer") as session:
        async with session.post("/join", data=pubkey) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to join network. Issuer error: {response.status}"
                )
            
            join_data = await response.text()

            async with tc_session.post("/join", data=join_data) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to join network: {response.status} {await response.text()}"
                    )

                long_term_pseudonym = await response.text()
                cred_manager.set_ltp(long_term_pseudonym)


async def main():
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, shutdown)
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, shutdown)

    try:
        async with aiohttp.ClientSession(
            f"http://{conf.env('TC_HOST')}:9090"
        ) as session:
            while True:
                # clean up
                cred_manager.clear()
                try:
                    for _ in range(q.qsize()):
                        q.get_nowait()
                except asyncio.QueueEmpty:
                    pass

                # sleep for a random amount of time
                await asyncio.sleep(utils.get_random_int(0, conf.env("JOIN_MAX_DELAY")))

                try:
                    await join(session)
                except Exception as e:
                    logging.error(f"JOIN error: {e}")
                    continue

                await broadcast_v2v.initialize()
                await broadcast_heartbeat.initialize()
                await broadcast_log.initialize()

                tasks = [
                    asyncio.create_task(heartbeat_receiver(session)),
                    asyncio.create_task(v2v_receiver(session)),
                    asyncio.create_task(message_generator(session)),
                    asyncio.create_task(pseudonym_refresher(session)),
                ]

                if conf.env("VEHICLE_MOVING"):
                    tasks.append(asyncio.create_task(movement_manager()))

                await exit_checker()
                for task in tasks:
                    task.cancel()

                broadcast_v2v.close()
                broadcast_heartbeat.close()
                broadcast_log.close()
                # clean memory
                gc.collect()

                if not conf.env("AUTO_REJOIN"):
                    await asyncio.sleep(999999999999)
    except asyncio.CancelledError:
        broadcast_v2v.close()
        broadcast_heartbeat.close()
        broadcast_log.close()


def shutdown():
    for task in asyncio.all_tasks():
        task.cancel()
    logging.info("Shutting down")


if __name__ == "__main__":
    log.configLogging()
    logging.debug("OBU running")
    logging.info(conf.env())
    logging.info(f"Multicast group: {broadcast_v2v}")
    asyncio.run(main())
