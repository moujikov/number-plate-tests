import os
from . import logging

development_mode = os.getenv('MODE', '').lower() == 'development'

if development_mode:
  logging.info('Running in development mode.')
