from environs import Env

## Environment variables ##

vars = {}

def parse_environment_vars():
    global vars

    env = Env()
    env.read_env()

    vars["HOSTNAME"]            = env.str("HOSTNAME")
    vars["LOG_LEVEL"]           = env.str("LOG_LEVEL", default="info")
    vars["LOG_TO_FILE"]         = env.bool("LOG_TO_FILE")
    vars["LOG_MAX_SIZE"]        = env.int("LOG_MAX_SIZE")
    vars["PSEUDONYM_SIZE"]      = env.int("PSEUDONYM_SIZE")

    vars["LOG_FILE_NAME"]       = f"/logs/{vars['HOSTNAME']}.log"

def env(variable=None):
    if variable is None:
        return vars

    return vars.get(variable)


parse_environment_vars()
