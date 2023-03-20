from datetime import datetime, timezone
import math

import conf

def get_freshness_parameter():  
    return int(math.floor(datetime.now(timezone.utc).timestamp()))

def get_prl_duration_time():
    return conf.env("T_PRL")