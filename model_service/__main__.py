import os

import uvicorn
from dotenv import load_dotenv

from model_service import asgi_app

load_dotenv()

# Get the port from the environment variable, default to 8000 if not set
port = int(os.getenv("PORT", 8000))

# Run the app with Uvicorn
uvicorn.run(asgi_app, host="0.0.0.0", port=port)
