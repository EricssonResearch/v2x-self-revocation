from quart import Quart, request
import logging
import signal
import asyncio

import utils
import crypto
import json
import log
import conf

app = Quart("Issuer")
ra_key = utils.read_from_file("/etc/credentials/ra_public.pem")
group_key = crypto.generate_group_key()

@app.route("/join", methods=["POST"])
async def join():
    # enroll a new vehicle to the network
    pubkey = await request.get_data()

    # create a long-term pseudonym identifier for the vehicle
    id = utils.generate_random_id(conf.env("PSEUDONYM_SIZE"))
    logging.debug(f"Generated new long-term ID: {id}")

    try:
        data = {
            "ltp" : id,
            "keyRA" : ra_key,
            "groupKey": group_key,
            "timestamp" : utils.get_freshness_parameter() 
        }

        return crypto.encrypt(pubkey, json.dumps(data))
    except Exception as e:
            logging.error(e)
            return str(e), 500


@app.before_serving
async def startup():
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, shutdown)
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, shutdown)


def shutdown():
    logging.info("Shutting down")


if __name__ == "__main__":
    log.configLogging()
    logging.debug("Issuer running.")
    logging.info(f"GROUP_KEY {group_key}")
    app.run(host="0.0.0.0", port=80)
