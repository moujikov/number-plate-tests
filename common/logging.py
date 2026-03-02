import logging
from .settings import development_mode

logging.basicConfig(
  level=(logging.DEBUG if development_mode else logging.INFO),
  format="%(asctime)s %(levelname)s - %(message)s",
  datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
