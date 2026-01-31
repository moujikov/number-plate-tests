import os
import uvicorn

uvicorn.run("rest_server_test.server:app",
            host=os.getenv('BIND', '0.0.0.0'),
            port=int(os.getenv('PORT', '8000')),
            reload=False)
