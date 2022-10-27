from environs import Env

## Environment variables ##

vars = {}

def parse_environment_vars():
    global vars

    env = Env()
    env.read_env()

    vars["HOSTNAME"]                    = env.str("HOSTNAME")
    vars["REPORT_MALICIOUS_ONLY"]       = env.bool("REPORT_MALICIOUS_ONLY")
    vars["REPORT_PERIOD"]               = env.float("REPORT_PERIOD") 
    vars["REPLAY_RATE"]                 = env.float("REPLAY_RATE")
    vars["LOG_LEVEL"]                   = env.str("LOG_LEVEL", default="info")
    vars["LOG_TO_FILE"]                 = env.bool("LOG_TO_FILE")
    vars["V2V_PORT"]                    = env.int("V2V_PORT", default=9000)
    vars["NUM_GROUPS"]                  = env.int("NUM_GROUPS", default=1)
    vars["USE_EPOCHS"]                  = env.bool("USE_EPOCHS")
    vars["T_V"]                         = env.int("T_V")
    vars["E_TOL"]                         = env.int("E_TOL")
    vars["T_E"]                         = env.int("T_E")

def env(variable=None):
    if variable is None:
        return vars

    return vars.get(variable)


parse_environment_vars()
