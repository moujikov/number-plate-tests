import os
import uvicorn

uvicorn.run("rest_server_test.server:app",
            host='0.0.0.0',
            port=os.environ.get("PORT", 8000),
            reload=False)
