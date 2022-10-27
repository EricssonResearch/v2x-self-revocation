import asyncio
import logging
import aiohttp
import random
import signal

import conf
import log
from broadcast import Broadcast

broadcast = Broadcast()

async def send_delayed(hb, delay):
    try:
        await asyncio.sleep(delay)
        await broadcast.send(hb)
    except asyncio.CancelledError:
        pass

async def broadcast_heartbeats():
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, shutdown)
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, shutdown)
    drop_rate = conf.env("RSU_DROP_RATE")
    delay_rate = conf.env("RSU_DELAY_RATE")
    t_t = conf.env("T_V")

    try:
        await broadcast.initialize()

        async with aiohttp.ClientSession() as session:
            while True:
                await asyncio.sleep(conf.env("HEARTBEAT_PERIOD"))

                try:
                    async with session.get('http://ra/heartbeat') as response:
                        if response.status != 200:
                            logging.error(f"Could not get heartbeat: {response.status}")
                            continue

                        hb = (await response.text()).encode()

                    p = random.random()

                    if p < drop_rate:
                        logging.debug("Dropping heartbeat")
                    elif p < drop_rate + delay_rate:
                        delay = random.randint(1, t_t)
                        logging.debug(f"Delaying heartbeat by {delay} seconds")
                        asyncio.create_task(send_delayed(hb, delay))
                    else:
                        logging.debug("Broadcast new heartbeat")
                        await broadcast.send(hb)

                except Exception as e:
                    logging.debug(f"broadcast_heartbeats: {e}")
    except asyncio.CancelledError:
        broadcast.close()

def shutdown():
    for task in asyncio.all_tasks():
        task.cancel()
    logging.info("Shutting down")


if __name__ == "__main__":
    log.configLogging()
    logging.debug("RSU running")
    logging.info(conf.env())
    asyncio.run(broadcast_heartbeats())
