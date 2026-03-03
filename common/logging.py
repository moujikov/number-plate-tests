import logging
from . import LOG_LEVEL


logging.basicConfig(
  level=LOG_LEVEL,
  format="%(asctime)s %(levelname)s - %(message)s",
  datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
