import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def info(message: str):
  logger.info(message)
  
def warning(message: str):
  logger.warning(message)
  
def error(message: str):
  logger.error(message)
