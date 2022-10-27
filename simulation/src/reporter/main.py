import asyncio
import logging
import aiohttp
import signal

import conf
import utils
from broadcast import Broadcast
import log

pseudonyms = []
reported_pseudonyms = []

async def replay_message(ps, broadcast, data):
    try:
        delay_time = utils.compute_delay_time()
        await asyncio.sleep(delay_time)
        logging.debug(f"Replaying msg from {ps} after {delay_time}s")
        await broadcast.send(data)
    except asyncio.CancelledError:
        pass

async def pseudonym_reporter():
    rate = conf.env("REPORT_PERIOD")

    try:
        async with aiohttp.ClientSession("http://ra") as session:
            while True:
                await asyncio.sleep(rate)
                if not pseudonyms:
                    continue

                ps = utils.get_random_element(pseudonyms)
                logging.debug(f"Reporting {ps}")

                try:
                    async with session.get(f'/revoke/{ps}') as response:
                        if response.status != 200:
                            logging.debug(f"pseudonym_reporter error: {response.status} {await response.text()}")
                    
                    pseudonyms.remove(ps)
                    reported_pseudonyms.append(ps)
                except Exception as e:
                    logging.debug(f"pseudonym_reporter: {e}")
    except asyncio.CancelledError:
        pass

async def v2v_replayer(index):
    try:
        rate = conf.env("REPLAY_RATE")
        port = conf.env("V2V_PORT") + index
        malicious_only = conf.env("REPORT_MALICIOUS_ONLY")

        broadcast = Broadcast(port, random_group=False)
        await broadcast.initialize()

        logging.debug(f"Multicast group: {broadcast}")

        while True:
            try:
                data = await broadcast.recv()

                token = utils.decode_jwt(data)
                ps = token["payload"]["iss"]
                malicious = token["payload"]["malicious"]

                if not malicious_only or malicious:
                    if ps not in pseudonyms and ps not in reported_pseudonyms:
                        pseudonyms.append(ps)

                    if rate > 0.0 and utils.roll_dice(rate):
                        asyncio.create_task(replay_message(ps, broadcast, data))
            except Exception as e:
                logging.error(f"v2v_receiver: {e}")

    except asyncio.CancelledError:
        broadcast.close()


async def main():
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, shutdown)
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, shutdown)

    try:
        for i in range(1, conf.env("NUM_GROUPS") + 1):
            asyncio.create_task(v2v_replayer(i))

        await pseudonym_reporter()
    except asyncio.CancelledError:
        pass


def shutdown():
    for task in asyncio.all_tasks():
        task.cancel()
    logging.info("Shutting down")


if __name__ == "__main__":
    log.configLogging()
    logging.debug("Attacker running")
    logging.info(conf.env())
    asyncio.run(main())
