"""
Starts the SAP Analyst ADK web server with:
  - DatabaseSessionService  → sessions + state persisted to SQLite (survive restarts)
  - InMemoryMemoryService   → cross-session semantic search (in-process)

Session state (tool_context.state) is written to SQLite so saved insights
persist across server restarts within the same session ID.
"""

from dotenv import load_dotenv
load_dotenv()

from google.adk.cli.fast_api import get_fast_api_app
import uvicorn

# SQLite with async driver — sessions and their state survive restarts
SESSION_DB = "sqlite+aiosqlite:///./sap_analyst_sessions.db"

app = get_fast_api_app(
    agents_dir=".",
    session_service_uri=SESSION_DB,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    web=True,
)

if __name__ == "__main__":
    print("Starting SAP Analyst with persistent sessions...")
    print(f"  Sessions + State → {SESSION_DB}")
    print(f"  Dev UI           → http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
