#!/bin/bash

# Configuration
export GOOGLE_CLOUD_PROJECT="multiagent-system-496514"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GOOGLE_CLOUD_LOCATION="global"

# A2A URLs (pointing to local ports)
export RESEARCHER_AGENT_CARD_URL="http://localhost:8001/a2a/Researcher/.well-known/agent-card.json"
export CRITIC_VALIDATOR_AGENT_CARD_URL="http://localhost:8002/a2a/critic_validator/.well-known/agent-card.json"
export STORY_TELLER_AGENT_CARD_URL="http://localhost:8003/a2a/Story_teller/.well-known/agent-card.json"

# Ensure imports work from the current directory
export PYTHONPATH=$PYTHONPATH:.

# Activate virtual environment
source .venv/bin/activate

echo "🚀 Starting Multi-Agent Microservices Locally..."

# 1. Start Researcher (Port 8001)
uvicorn sap_analyst.Researcher:app --host 0.0.0.0 --port 8001 &
RESEARCHER_PID=$!
echo "✓ Researcher started on port 8001 (PID: $RESEARCHER_PID)"

# 2. Start Critic Validator (Port 8002)
uvicorn sap_analyst.critic_validator:app --host 0.0.0.0 --port 8002 &
CRITIC_PID=$!
echo "✓ Critic Validator started on port 8002 (PID: $CRITIC_PID)"

# 3. Start Story Teller (Port 8003)
uvicorn sap_analyst.Story_teller:app --host 0.0.0.0 --port 8003 &
STORY_PID=$!
echo "✓ Story Teller started on port 8003 (PID: $STORY_PID)"

# 4. Start Orchestrator (Port 8000)
# We use port 8000 for the main UI/Orchestrator entry point
uvicorn sap_analyst.orchestrator:app --host 0.0.0.0 --port 8000 &
ORCH_PID=$!
echo "✓ Orchestrator started on port 8000 (PID: $ORCH_PID)"

echo "------------------------------------------------------"
echo "ADK Dev UI: http://localhost:8000"
echo "Press Ctrl+C to stop all processes."
echo "------------------------------------------------------"

# Trap SIGINT (Ctrl+C) and kill background processes
trap "kill $RESEARCHER_PID $CRITIC_PID $STORY_PID $ORCH_PID; exit" SIGINT

# Wait for all processes to finish
wait
