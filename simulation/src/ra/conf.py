from environs import Env

CLEANER_PERIOD = 0.5

## Environment variables ##

vars = {}

def parse_environment_vars():
    global vars

    env = Env()
    env.read_env()

   
    vars["T_V"]                         = env.int("T_V")

    vars["HOSTNAME"]                    = env.str("HOSTNAME")
    vars["LOG_LEVEL"]                   = env.str("LOG_LEVEL", default="info")
    vars["LOG_TO_FILE"]                 = env.bool("LOG_TO_FILE")
    vars["LOG_MAX_SIZE"]                = env.int("LOG_MAX_SIZE")
    vars["HEARTBEAT_PERIOD"]            = env.float("HEARTBEAT_GENERATION_PERIOD")
    vars["TC_STORE_LAST_PRL"]           = env.bool("TC_STORE_LAST_PRL")

    vars["LOG_FILE_NAME"]               = f"/logs/{vars['HOSTNAME']}.log"

    # compute other parameters
    if vars["TC_STORE_LAST_PRL"]:
        vars["T_PRL"] = vars["T_V"] + vars["T_V"] # T_eff
    else:
        vars["T_PRL"] = vars["T_V"] # T_prl

def env(variable=None):
    if variable is None:
        return vars

    return vars.get(variable)


parse_environment_vars()
