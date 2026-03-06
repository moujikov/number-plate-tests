import uvicorn

from common import SYSTEM_LOG_LEVEL

from . import HOST, PORT
from .server import app

uvicorn.run(app,
            host=HOST,
            port=PORT,
            server_header=False,
            access_log=False,
            log_level=SYSTEM_LOG_LEVEL.lower(),
            reload=False)
