from environs import Env

CLEANER_PERIOD = 0.5

## Environment variables ##

vars = {}

def parse_environment_vars():
    global vars

    env = Env()
    env.read_env()

   
    vars["T_R"]                         = env.int("T_R")
    vars["T_V"]                         = env.int("T_V")
    vars["T_E"]                         = env.int("T_E")
    vars["E_TOL"]                         = env.int("E_TOL")

    vars["HOSTNAME"]                    = env.str("HOSTNAME")
    vars["USE_EPOCHS"]                  = env.bool("USE_EPOCHS")
    vars["LOG_LEVEL"]                   = env.str("LOG_LEVEL", default="info")
    vars["LOG_TO_FILE"]                 = env.bool("LOG_TO_FILE")  
    vars["HEARTBEAT_PERIOD"]            = env.float("HEARTBEAT_GENERATION_PERIOD")
    vars["TC_STORE_LAST_PRL"]           = env.bool("TC_STORE_LAST_PRL")

    # compute other parameters
    if vars["TC_STORE_LAST_PRL"]:
        vars["T_PRL"] = vars["T_R"] + vars["T_V"] + vars["T_V"] # T_eff
    else:
        vars["T_PRL"] = vars["T_R"] + vars["T_V"] # T_prl

    vars["E_PRL"] = vars["E_TOL"] + 2

def env(variable=None):
    if variable is None:
        return vars

    return vars.get(variable)


parse_environment_vars()
