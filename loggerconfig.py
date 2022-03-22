import logging 
import logging.config

def getLogger(name):
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    return logging.getLogger(name)