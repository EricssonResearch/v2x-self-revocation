from environs import Env

## Environment variables ##

vars = {}

def parse_environment_vars():
    global vars

    env = Env()
    env.read_env()

    vars["HOSTNAME"]                = env.str("HOSTNAME")
    vars["HEARTBEAT_PERIOD"]        = env.float("HEARTBEAT_DISTRIBUTION_PERIOD")
    vars["LOG_LEVEL"]               = env.str("LOG_LEVEL", default="info")
    vars["LOG_TO_FILE"]             = env.bool("LOG_TO_FILE")  
    vars["HEARTBEAT_PORT"]          = env.int("HEARTBEAT_PORT", default=8000)
    vars["RSU_DROP_RATE"]           = env.float("RSU_DROP_RATE")
    vars["RSU_DELAY_RATE"]          = env.float("RSU_DELAY_RATE")
    vars["T_V"]                     = env.int("T_V")

def env(variable=None):
    if variable is None:
        return vars

    return vars.get(variable)


parse_environment_vars()
