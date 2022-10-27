from environs import Env

## Environment variables ##

vars = {}

def parse_environment_vars():
    global vars

    env = Env()
    env.read_env()

    vars["HOSTNAME"]                    = env.str("HOSTNAME")
    vars["LOG_LEVEL"]                   = env.str("LOG_LEVEL", default="info")
    vars["LOG_TO_FILE"]                 = env.bool("LOG_TO_FILE")  
    vars["USE_EPOCHS"]                  = env.bool("USE_EPOCHS")
    vars["TC_HOST"]                     = env.str("TC_HOST", default="localhost")
    vars["PSEUDONYM_REFRESH_PERIOD"]    = env.float("PSEUDONYM_REFRESH_PERIOD")
    vars["V2V_GENERATION_PERIOD"]       = env.float("V2V_GENERATION_PERIOD")
    vars["HEARTBEAT_PERIOD"]            = env.float("HEARTBEAT_DISTRIBUTION_PERIOD")
    vars["NUM_PSEUDONYMS"]              = env.int("NUM_PSEUDONYMS")
    vars["HEARTBEAT_PORT"]              = env.int("HEARTBEAT_PORT", default=8000)
    vars["V2V_PORT"]                    = env.int("V2V_PORT", default=9000)
    vars["NUM_GROUPS"]                  = env.int("NUM_GROUPS", default=1)
    vars["ATTACKER_LEVEL"]              = env.str("ATTACKER_LEVEL", default="random")
    vars["VEHICLE_MALICIOUS"]           = env.bool("VEHICLE_MALICIOUS")
    vars["T_V"]                         = env.int("T_V")
    vars["T_R"]                         = env.int("T_R")
    vars["E_TOL"]                         = env.int("E_TOL")
    vars["T_E"]                         = env.int("T_E") 
    vars["JOIN_MAX_DELAY"]              = env.int("JOIN_MAX_DELAY")
    vars["BLIND_ATTACKER_DROP_RATE"]    = env.float("BLIND_ATTACKER_DROP_RATE")
    vars["BLIND_2_ATTACKER_DELAYED"]    = env.bool("BLIND_2_ATTACKER_DELAYED")

def env(variable=None):
    if variable is None:
        return vars

    return vars.get(variable)


parse_environment_vars()
