import logging
from time import gmtime
from logging.config import dictConfig
import sys
import os

import conf

def parse_log_level(level):
    l = level.lower()

    if l == "debug":
        return logging.DEBUG
    if l == "info":
        return logging.INFO
    if l == "warning":
        return logging.WARNING
    if l == "error":
        return logging.ERROR
    if l == "critical":
        return logging.CRITICAL
    
    raise Exception("Error while parsing log level")

def configLogging():
    logging.addLevelName(logging.CRITICAL, 'critical')
    logging.addLevelName(logging.ERROR, 'error')
    logging.addLevelName(logging.WARNING, 'warning')
    logging.addLevelName(logging.INFO, 'info')
    logging.addLevelName(logging.DEBUG, 'debug')

    if not os.path.exists("/logs"):
        os.mkdir("/logs", mode=0o750)

    if conf.env("LOG_TO_FILE"):
        logging.basicConfig(
            format='time="%(asctime)s" level=%(levelname)s msg="%(message)s"',
            level=parse_log_level(conf.env("LOG_LEVEL")),
            datefmt="%Y-%m-%dT%H:%M:%SZ",
            filename=f"/logs/{conf.env('HOSTNAME')}-obu.log",
            filemode="a",
        )
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    else:
        logging.basicConfig(
            format='time="%(asctime)s" level=%(levelname)s msg="%(message)s"',
            level=parse_log_level(conf.env("LOG_LEVEL")),
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )

    logging.Formatter.converter = gmtime

    dictConfig({
        'version': 1,
        'loggers': {
            'quart.app': {
                'level': 'ERROR',
            },
            'quart.serving': {
                'level': 'ERROR',
            },
        },
    })
