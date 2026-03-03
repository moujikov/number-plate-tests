import uvicorn

from . import HOST, PORT
from .server import app

uvicorn.run(app,
            host=HOST,
            port=PORT,
            server_header=False,
            access_log=False,
            reload=False)
