from quart import Quart, render_template
import logging
import signal
import asyncio
import aiohttp

import log
import conf
import utils
import regex_parser
from broadcast import Broadcast
from pseudonym import Pseudonym

app = Quart("V2X dashboard")
tasks = []
pseudonyms = {}
heartbeat = {}

async def map_cleaner():
    global pseudonyms
    try:
        while True:
            await asyncio.sleep(300)

            pseudonyms = {
                k:v for k,v in pseudonyms.items() 
                    if not v.is_unused()
            }
    except asyncio.CancelledError:
        pass


async def heartbeat_fetcher():
    global heartbeat

    try:
        async with aiohttp.ClientSession("http://ra") as session:
            while True:
                await asyncio.sleep(1)
                try:
                    hb, result = await utils.get_heartbeat(session)
                    if result != 200:
                        logging.warning(f"Failed to get heartbeat: {result}")
                    else:
                        heartbeat = hb
                except Exception as e:
                    logging.error(f"heartbeat_fetcher: {e}")
    except asyncio.CancelledError:
        pass


async def group_listener(index):
    try:
        logging.debug(f"Group listener {index}")
        port = conf.env("LOG_PORT") + index
        broadcast = Broadcast(port, random_group=False)
        await broadcast.initialize()

        logging.debug(f"Multicast group: {broadcast}")

        while True:
            try:
                data = (await broadcast.recv()).decode("utf-8")
                #logging.debug(data)

                if data.startswith("SIGN"):
                    ps, malicious = regex_parser.parse_sign(data)
                    #logging.debug(f"Parsed: {ps} {malicious}")
                    if ps in pseudonyms:
                        pseudonyms[ps].update_last_seen()
                        pseudonyms[ps].group = index
                    else:
                        pseudonyms[ps] = Pseudonym(ps, index, malicious)

                elif data.startswith("VERIFY"):
                    affected = regex_parser.parse_verify(data)
                    #logging.debug(f"Parsed: {affected_ps}")
                    for ps in affected:
                        if ps in pseudonyms:
                            pseudonyms[ps].update_last_malicious()

            except Exception as e:
                logging.error(f"group_listener: {e}")

    except asyncio.CancelledError:
        broadcast.close()

@app.route("/revoke/<id>")
async def revoke(id):
    if id in pseudonyms:
        return await pseudonyms[id].revoke()

    return "Pseudonym does not exist", 400

@app.route("/heartbeat")
async def heartbeat():
    return heartbeat

@app.route("/refresh", methods=["get"])
async def refresh():
    ps = {
        k : v.to_dict()
            for k,v in pseudonyms.items() 
            if not v.is_unused() and v.update_status()
    }

    return {
        "ps": ps,
        "hb": heartbeat
    }

@app.route("/", methods=["GET"])
async def main():
    return await render_template(
        'main.html', 
        title="V2X Dashboard",
        groups=conf.env("NUM_GROUPS"),
        t_eff=conf.env("T_EFF")
    )

@app.before_serving
async def startup():
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, shutdown)
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, shutdown)

    for i in range(1, conf.env("NUM_GROUPS") + 1):
            tasks.append(asyncio.create_task(group_listener(i)))

    tasks.append(asyncio.create_task(map_cleaner()))
    tasks.append(asyncio.create_task(heartbeat_fetcher()))

def shutdown():
    for task in tasks:
        task.cancel()
    logging.info("Shutting down")

if __name__ == "__main__":
    log.configLogging()
    logging.debug("Web running.")
    logging.info(conf.env())
    app.run(host="0.0.0.0", port=80)
