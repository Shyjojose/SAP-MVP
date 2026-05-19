from pathlib import Path
from google.adk.cli.fast_api import get_fast_api_app
from .agent import root_agent

# Expose an ASGI `app` so `uvicorn sap_analyst.orchestrator:app` works.
agents_dir = "sap_analyst"
# Orchestrator should serve the web UI (ADK Dev UI) so `web=True`.
app = get_fast_api_app(agents_dir=agents_dir, web=True, a2a=True)
