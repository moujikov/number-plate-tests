import os
import uvicorn
from .server import app

uvicorn.run(app,
            host=os.getenv('BIND', '0.0.0.0'),
            port=int(os.getenv('PORT', '8000')),
            reload=False)
