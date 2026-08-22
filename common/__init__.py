import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING').upper()
SYSTEM_LOG_LEVEL = os.getenv('SYSTEM_LOG_LEVEL', 'WARNING').upper()
TZ = os.getenv('TZ', 'UTC')

from .logging import logger
logger.info(f'------------ STARTING UP ------------')
logger.info(f'App log level: {LOG_LEVEL}, system log level: {SYSTEM_LOG_LEVEL}')
logger.info(f'Using timezone {TZ}')
