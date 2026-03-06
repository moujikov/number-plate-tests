import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
SYSTEM_LOG_LEVEL = os.getenv('SYSTEM_LOG_LEVEL', 'WARNING').upper()

from .logging import logger
logger.info(f'------ STARTING UP, LOG_LEVEL: {LOG_LEVEL}, SYSTEM_LOG_LEVEL: {SYSTEM_LOG_LEVEL} ------')
