from quart import Quart
import asyncio
import logging
import signal

from crypto import Ecdsa
from prl import PRL
import conf
import freshness
import log

app = Quart("RA")
ra_key = Ecdsa.load("/etc/credentials/ra_private.pem", None)
prl = PRL(ra_key)
tasks = []

async def prl_cleaner():
    try:
        while True:
            await asyncio.sleep(conf.CLEANER_PERIOD)
            #logging.debug("Removing expired pseudonyms from PRL")
            prl.remove_old_pseudonyms()
    except asyncio.CancelledError:
        pass

async def epoch_manager():
    try:
        if not conf.env("USE_EPOCHS"):
            return
        
        while True:
            await asyncio.sleep(conf.env("T_E"))
            logging.info(f"EPOCH {freshness.advance_epoch()}")
    except asyncio.CancelledError:
        pass

async def heartbeat_generator():
    try:
        while True:
            await asyncio.sleep(conf.env("HEARTBEAT_PERIOD"))
            #logging.debug("Generating new heartbeat")
            prl.generate_heartbeat()
    except asyncio.CancelledError:
        pass

@app.route("/heartbeat")
async def heartbeat():
    #logging.debug("Sending out heartbeat")
    return prl.get_heartbeat()

@app.route("/revoke/<id>")
async def revoke(id):
    if prl.add_pseudonym(id):
        logging.info(f"REVOKE {id}")
        return f"{id} revoked.\n"
    else:
        return f"{id} already in PRL\n"

@app.route("/report/<id>")
async def report(id):
    logging.info(f"REPORT {id}")
    # TODO report a pseudonym
    return f"{id} reported.\n"

@app.route("/freshness")
async def get_freshness_parameter():
    fre = freshness.get_freshness_parameter()
    logging.debug(f"Sending freshness parameter {fre}")
    return str(fre)

@app.before_serving
async def startup():
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, shutdown)
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, shutdown)

    tasks.append(asyncio.create_task(prl_cleaner()))
    tasks.append(asyncio.create_task(epoch_manager()))
    tasks.append(asyncio.create_task(heartbeat_generator()))


def shutdown():
    for task in tasks:
        task.cancel()
    logging.info("RA STOP")


if __name__ == "__main__":
    log.configLogging()
    logging.info("RA START")
    logging.info(conf.env())
    app.run(host="0.0.0.0", port=80)
