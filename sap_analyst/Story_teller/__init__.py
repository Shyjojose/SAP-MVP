from pathlib import Path
from google.adk.cli.fast_api import get_fast_api_app

# Expose an ASGI `app` so `uvicorn sap_analyst.Story_teller:app` works.
agents_dir = "sap_analyst"
app = get_fast_api_app(agents_dir=agents_dir, web=False, a2a=True)
