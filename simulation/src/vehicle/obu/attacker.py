import aiohttp
import logging
import random
import asyncio
from enum import IntEnum

import utils
import conf

class AttackerLevel(IntEnum):
    HONEST      = 0
    NAIVE       = 1
    BLIND_1     = 2
    BLIND_2     = 3
    BLIND_3     = 4
    SMART       = 5
    SMARTER     = 6

    def from_str(lvl):
        lvl = lvl.lower()
        if lvl == "honest":
            return AttackerLevel.HONEST
        if lvl == "naive":
            return AttackerLevel.NAIVE
        if lvl == "blind-1" or lvl == "blind_1":
            return AttackerLevel.BLIND_1
        if lvl == "blind" or lvl == "blind-2" or lvl == "blind_2":
            return AttackerLevel.BLIND_2
        if lvl == "blind-3" or lvl == "blind_3":
            return AttackerLevel.BLIND_3
        if lvl == "smart":
            return AttackerLevel.SMART
        if lvl == "smarter":
            return AttackerLevel.SMARTER
        if lvl == "random":
            return AttackerLevel(random.randint(0, 6))
        
        raise Exception(f"Invalid attacker level: {lvl}")

class Attacker():
    def __init__(self, level, session, cred_manager, q):
        self.__level = AttackerLevel.from_str(level)
        self.__session = session
        self.__cred_manager = cred_manager
        self.__q = q
        self.__last_sent = 0

    async def process_heartbeat(self, hb):
        if self.__level == AttackerLevel.HONEST:
            # always relay all heartbeats immediately
            return await self.__send(hb)

        if self.__level == AttackerLevel.NAIVE:
            # always drop heartbeats
            return await self.__drop(hb)

        if self.__level == AttackerLevel.BLIND_1:
            # drop a % of heartbeats, delay others
            rate = conf.env("BLIND_ATTACKER_DROP_RATE")
            return await self.__blind_send(hb, rate)

        if self.__level == AttackerLevel.BLIND_2:
            # relay only one heartbeat per T_R (or T_E * (E_TOL + 1))
            if conf.env("USE_EPOCHS"):
                delay_on = False
                max_delay = conf.env("T_E") * (conf.env("E_TOL") + 1)
                delay = 0
            else:
                delay_on = conf.env("BLIND_2_ATTACKER_DELAYED")
                max_delay = conf.env("T_R")
                delay = utils.get_random_int(1, conf.env("T_V") - 1) if delay_on else 0

            now = utils.get_timestamp()
            if now - self.__last_sent >= max_delay - delay - 1:
                self.__last_sent = now + delay
                if delay_on:
                    asyncio.create_task(self.__send_delayed(hb, delay))
                    return True
                else:
                    return await self.__send(hb)
            else:
                return await self.__drop(hb)

        if self.__level == AttackerLevel.BLIND_3:
            # always delay
            if conf.env("USE_EPOCHS"):
                delay = utils.get_random_int(1, conf.env("T_E") * (conf.env("E_TOL") + 1))
            else:
                delay = utils.get_random_int(1, conf.env("T_V") - 1)

            asyncio.create_task(self.__send_delayed(hb, delay))
            return True

        if self.__level in [AttackerLevel.SMART, AttackerLevel.SMARTER]:
            decoded_hb = utils.decode_jwt(hb)
            ltp = self.__cred_manager.get_ltp()
            pseudonyms = self.__cred_manager.get_pseudonyms()

            # drop heartbeat if either LTP or a pseudonym is revoked
            for pseudonym in decoded_hb["payload"]["prl"]:
                if pseudonym == ltp or pseudonym in pseudonyms:
                    return await self.__drop(hb)

            # otherwise, relay immediately if SMART or postpone if SMARTER
            if self.__level == AttackerLevel.SMART or conf.env("USE_EPOCHS"):
                return await self.__send(hb)
            else:
                ts = decoded_hb["payload"]["iat"]
                delay = utils.compute_remaining_time(ts)
                asyncio.create_task(self.__send_delayed(hb, delay))
                return await self.__send(hb) # send twice for best results

        raise Exception(f"process_heartbeat not implemented for {self.__level.name}")

    async def __blind_send(self, hb, rate):
        # this attacker does not make sense with epochs
        if conf.env("USE_EPOCHS"):
            return await self.__drop(hb)

        t_r = conf.env("T_R")
        t_t = conf.env("T_V")
        hb_period = conf.env("HEARTBEAT_PERIOD")

        # number of heartbeats per T_R
        hbs_per_t_r = int(t_r // hb_period)

        # drop "rate" percentage of heartbeats
        if utils.get_random_int(1, hbs_per_t_r) <= int(hbs_per_t_r * rate):
            return await self.__drop(hb)
        
        # delay by T_V - 1 (to avoid TC dropping the hb because too old)
        asyncio.create_task(self.__send_delayed(hb, t_t - 1))
        return True

    async def __send(self, hb):
        try:
            logging.debug("Relaying heartbeat")
            async with self.__session.post("/heartbeat", data=hb) as response:
                if response.status == 403:
                    self.__q.put_nowait(True)
                elif response.status != 200:
                    logging.debug(
                        f"TC/heartbeat failed: {response.status} {await response.text()}".strip()
                    )
                return True
        except aiohttp.ServerDisconnectedError:
            logging.error("TC: ServerDisconnectedError")
            return False

    async def __send_delayed(self, hb, delay):
        try:
            await asyncio.sleep(delay)
            await self.__send(hb)
        except asyncio.CancelledError:
            pass

    async def __drop(self, _):
        logging.debug("Dropping heartbeat")
        return True