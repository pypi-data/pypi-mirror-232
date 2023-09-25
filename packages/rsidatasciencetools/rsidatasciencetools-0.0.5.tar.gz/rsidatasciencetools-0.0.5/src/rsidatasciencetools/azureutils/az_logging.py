import sys
from pathlib import Path
from os import path, remove
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from logging import handlers
import time
# from datetime import datetime
# import pytz
from rsidatasciencetools.utils import log_level_dict


global global_level, env_g
global_level = logging.ERROR
env_g = None
# fmt = '%(asctime)sUTC - %(name)10s: [%(levelname)8s] %(message)s'
fmt = "%(asctime)sUTC [%(filename)s:%(lineno)s-%(funcName)12s()|%(levelname)8s] %(message)s"

DEFAULT_LOGFILE_NAME = 'dst_logging'


def set_all_loggers_level(level=global_level):
    global global_level, env_g
    level = (env_g.get('LOG_LEVEL','WARNING') 
        if level is None and env_g is not None else level)
    for logger in logging.Logger.manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            logger.setLevel(level)
    global_level = level

def get_log_file(name, aggregate_logfile):
    global env_g
    log_file = env_g.get('LOG_FILE', None)
    if log_file is None:
        log_path = env_g.get('CONFIG_PATH', None)
        assert log_path is not None, 'the logging path is not defined'
        log_file = path.join(log_path, 
            f'{name if aggregate_logfile is None else aggregate_logfile}.log')
    return log_file


def get_az_logger(name, level=None, env=None, to_file=False, restart=False, 
        get_log_filename=False, aggregate_logfile=DEFAULT_LOGFILE_NAME):
    global env_g
    if env is None:
        if env_g is None:
            from rsidatasciencetools.config.baseconfig import env
            env_g = env
        env = env_g
    elif env_g is None:
        env_g = env
    AZURE_APP_INSIGHTS = env.get('AZURE_APP_INSIGHTS', None)
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger(name)
    log_file = None
    to_file = bool(env.get('LOG_TO_FILE', env.get('LOG_FILE', to_file)))
    if to_file:
        has_handler = [isinstance(h, handlers.RotatingFileHandler) 
            for h in logger.handlers]
        log_file = get_log_file(name, aggregate_logfile)
        restart and path.exists(log_file) and remove(log_file)
        print(f'writing logs to: {log_file} [exists: {path.exists(log_file)}]')
        file_handler = handlers.RotatingFileHandler(
            filename=log_file,
            mode='a',
            maxBytes=2*10**20,
            backupCount=10,
            encoding='utf-8')
        
        file_handler.setFormatter(logging.Formatter(fmt))
        # add handlers to logger
        if any(has_handler):
            idx = [i for i, ah in enumerate(has_handler) if ah][0]
            logger.handlers[idx] = file_handler
        else:
            # print('adding new file handler')
            logger.addHandler(file_handler)
    
    if env.get('LOG_TO_STDOUT',True):
        has_handler = [isinstance(h, logging.StreamHandler) 
            for h in logger.handlers]
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(logging.Formatter(fmt))
        if any(has_handler):
            idx = [i for i, ah in enumerate(has_handler) if ah][0]
            logger.handlers[idx] = stream
        else:
            # print('adding new stream handler')
            logger.addHandler(stream)
    
    if AZURE_APP_INSIGHTS is not None:
        has_handler = [isinstance(h, AzureLogHandler)
            for h in logger.handlers]
        handler = AzureLogHandler(connection_string=AZURE_APP_INSIGHTS)
        handler.setFormatter(logging.Formatter('%(process)10d - ' + fmt))
        if any(has_handler):
            idx = [i for i, ah in enumerate(has_handler) if ah][0]
            logger.handlers[idx] = handler
        else:
            logger.addHandler(handler)
    logger.warning(f'"{name}" logging started')
    if level is None:
        logger.setLevel(global_level)
    else:
        logger.setLevel(log_level_dict[level])

    if get_log_filename:
        return logger, log_file
    return logger
