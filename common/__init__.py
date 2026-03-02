from .settings import development_mode
from .logging import logger

if development_mode:
  logger.debug('Running in development mode.')
