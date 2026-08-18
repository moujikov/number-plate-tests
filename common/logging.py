import logging
from . import LOG_LEVEL, SYSTEM_LOG_LEVEL


logging.basicConfig(
  level=SYSTEM_LOG_LEVEL,
  format="%(asctime)s %(levelname)s - %(message)s",
  datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger("number_plates")
logger.setLevel(LOG_LEVEL)
