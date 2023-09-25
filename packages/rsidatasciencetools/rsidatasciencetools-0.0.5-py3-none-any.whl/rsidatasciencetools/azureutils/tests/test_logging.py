import logging
import os
from rsidatasciencetools.azureutils.az_logging import get_az_logger


def test_logger():
    logger1, logfile = get_az_logger('module1', restart=True, 
        to_file=True, get_log_filename=True, aggregate_logfile='data')
    logger2 = get_az_logger('module2', to_file=True, aggregate_logfile='data')
    logger2.setLevel(logging.INFO)
    logger1.warning('test - message 1a')
    logger1.critical('test - message 1b')
    logger2.debug('test - message 2a')
    logger2.info('test - message 2b')

    with open(logfile,'r') as f:
        lines = f.read().split()
    check = ['module1: [ WARNING] "module1" logging started',
             'module2: [ WARNING] "module2" logging started',
             'module1: [ WARNING] test - message 1a',
             'module1: [CRITICAL] test - message 1b',
             'module2: [   DEBUG] test - message 2a',
             'module2: [    INFO] test - message 2b']
    lines = [ln.split('-')[1].strip() for ln in lines]

    try:
        os.remove(logfile)
    except:
        pass

    assert all([ln == ck for ln, ck in zip(lines, check)])