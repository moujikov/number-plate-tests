import os

from common.logging import logger


HOST = os.getenv('BIND', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
logger.info(f'Listening on {HOST}:{PORT}')
