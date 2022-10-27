from datetime import datetime, timezone
import math

import conf

EPOCH_ID = 0

def advance_epoch():
    global EPOCH_ID
    EPOCH_ID += 1
    return EPOCH_ID

def get_freshness_parameter():
    if conf.env("USE_EPOCHS"):
        return EPOCH_ID
    
    return int(math.floor(datetime.now(timezone.utc).timestamp()))

def get_prl_duration_time():
    if conf.env("USE_EPOCHS"):
        return conf.env("E_PRL")

    return conf.env("T_PRL")