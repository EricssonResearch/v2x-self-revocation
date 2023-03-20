import logging
from time import gmtime
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
import os

import conf

fmt = 'time="%(asctime)s" level=%(levelname)s msg="%(message)s"'
fmt_date = "%Y-%m-%dT%H:%M:%SZ"

class FileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        RotatingFileHandler.__init__(self, *args, **kwargs)
        formatter = logging.Formatter(fmt, fmt_date)
        formatter.converter = gmtime
        self.setFormatter(formatter)


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

    logging.basicConfig(
        level=parse_log_level(conf.env("LOG_LEVEL")),
        datefmt=fmt_date,
        format=fmt
    )
    logging.Formatter.converter = gmtime

    if conf.env("LOG_TO_FILE"):
        handler = FileHandler(
            conf.env("LOG_FILE_NAME"),
            maxBytes=conf.env("LOG_MAX_SIZE")**20,
            backupCount=1
        )
        logging.getLogger().addHandler(handler)

    dictConfig({
        'version': 1,
        'loggers': {
            'quart.app': {
                'level': 'ERROR',
            },
            'quart.serving': {
                'level': 'ERROR',
            }
        },
    })
