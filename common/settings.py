import os

development_mode = os.getenv('MODE', '').lower() == 'development'
