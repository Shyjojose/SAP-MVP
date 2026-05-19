import os
from dotenv import load_dotenv

# Use ADK helper to build a FastAPI app that exposes the ADK Web UI/API
from google.adk.cli.fast_api import get_fast_api_app

# Load environment variables from .env
load_dotenv()

# Build the FastAPI app using the local `sap_analyst` agents directory.
# `web=True` serves the dev UI; `a2a=True` enables Agent-to-Agent endpoints.
app = get_fast_api_app(agents_dir="sap_analyst", web=True, a2a=True, host="0.0.0.0", port=8010)

if __name__ == "__main__":
    import uvicorn
    print("Starting SAP Analyst MVP on http://0.0.0.0:8010")
    uvicorn.run(app, host="0.0.0.0", port=8010)
