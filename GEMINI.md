# SAP Analyst MVP - Project Context

This project is an AI-powered SAP procurement analyst built with the **Google Agent Development Kit (ADK)** and **Vertex AI (Gemini 2.5 Flash)**. It implements a multi-agent system to autonomously query SAP tables, validate data, and deliver business-ready supply chain insights.

## Project Overview

- **Goal:** Provide autonomous supply chain insights from SAP data using natural language.
- **Framework:** Google ADK (Agent Development Kit).
- **Core LLM:** Gemini 2.0 Flash.
- **Use Case:** Master Thesis on "Autonomous Generation of Multi-Agent Systems for Supply Chain Planning".

## Architecture

The system uses a sequential multi-agent pipeline:

1.  **sap_analyst (Root Orchestrator):** Immediately delegates all user queries to the `Critic_validator`. It never asks clarifying questions.
2.  **Critic_validator (Data Auditor):**
    - Discovers table schemas (EKKO, EKPO, MARA).
    - Queries mock SAP tables via custom tools.
    - Performs sanity checks and data validation.
    - Passes 'APPROVED' data to the `Story_teller`.
3.  **Story_teller (Business Narrator):**
    - Translates raw JSON data into a plain-English narrative.
    - Avoids technical jargon and code.
    - Provides actionable business recommendations.

## Tech Stack

- **Agent Framework:** `google-adk==1.26.0`
- **Generative AI:** `google-genai`, `google-cloud-aiplatform` (Gemini 2.0 Flash)
- **Web Server:** `fastapi`, `uvicorn`
- **Database/Persistence:** `SQLAlchemy`, `aiosqlite` (SQLite for session persistence)
- **Configuration:** `python-dotenv`

## Getting Started

### Prerequisites
- Python 3.11+
- GCP Project with Vertex AI enabled.
- Authenticated `gcloud` CLI.

### Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the root:
```env
GOOGLE_GENAI_USE_VERTEXAI="true"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
```

### Running the System
```bash
python run.py
```
- **Dev UI:** http://127.0.0.1:8000
- **Sessions:** Persisted in `sap_analyst_sessions.db`.

## Development Conventions

### 1. Agent Definitions
Agents are defined in their respective directories using the `google.adk.agents.Agent` class.
- `sap_analyst/agent.py`: Root agent.
- `sap_analyst/subagents/Critic_validator/agent.py`: Validator agent.
- `sap_analyst/subagents/Story_teller/agent.py`: Narrator agent.

### 2. Tool Implementation
Tools are implemented as standard Python functions and wrapped with `google.adk.tools.FunctionTool`.
- See `sap_analyst/subagents/Critic_validator/tools.py` for examples like `query_sap_table` and `get_table_schema`.

### 3. Mock SAP Schema
The system simulates SAP HANA tables using in-memory dictionaries:
- **EKKO:** Purchasing Document Header.
- **EKPO:** Purchasing Document Item.
- **MARA:** General Material Data.
- **MARD:** Storage Location Data.

### 4. Session Management
Session state is persisted across restarts using SQLite. The `run.py` script configures `DatabaseSessionService` for this purpose.

## Project Structure

- `run.py`: Entry point starting the ADK FastAPI server.
- `sap_analyst/`: Main package for agents and logic.
  - `agent.py`: Root orchestrator.
  - `memory.py`: Shared memory tools (optional).
  - `subagents/`: Specialized agent implementations.
    - `Critic_validator/`: Logic for data auditing and SAP interaction.
    - `Story_teller/`: Logic for business reporting.
- `requirements.txt`: Project dependencies.
- `sap_analyst_sessions.db`: SQLite database for persistent sessions (generated at runtime).
