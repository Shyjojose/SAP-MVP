# SAP Analyst MVP — Google ADK Multi-Agent System

An AI-powered SAP procurement analyst built with the **Google Agent Development Kit (ADK)** and **Vertex AI (Gemini 2.5 Flash)**. This system implements a sophisticated multi-agent pipeline to autonomously query SAP tables, validate data, and deliver business-ready supply chain insights through a natural language interface.

> This MVP serves as a proof-of-concept for the Master Thesis topic: **"Autonomous Generation of Multi-Agent Systems for Supply Chain Planning"** at SAP's Supply Chain Management (SCM) Data Science team.

---

## 🏗 Architecture & Agentic Workflow

The system utilizes a hybrid **Agent-to-Agent (A2A)** architecture, where specialized agents communicate via the A2A protocol. Each agent operates as an independent microservice.

### Workflow Diagram

```text
[ User Query ]
      │
      ▼
┌───────────────┐
│  Orchestrator │ (Master Router)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Researcher    
│   (sql query) │◄─────────────────┐ (If Validation Fails)
└───────┬───────┘                  │
        │ (Raw Data Output)        │
        ▼                          │
┌───────────────┐                  │
│    Critic     ├─[Failed Check]───┘
│   Validator   │
└───────┬───────┘
        │ [Passed / STATUS: VALIDATED]
        ▼
┌───────────────┐
│ Story Teller  │ (Generates Human Insights)
└───────┬───────┘
        │
        ▼
[ Executive Report ]
```

### Core Components

1.  **Orchestrator (Port 8000):** Manages the high-level research loop and delegates tasks to specialized sub-agents.
2.  **Researcher (Port 8001):** Equipped with SAP-specific tools to discover table schemas and extract data from the mock SAP environment.
3.  **Critic Validator (Port 8002):** A strict data governance auditor that evaluates data for logical flaws and business logic sanity.
4.  **Story Teller (Port 8003):** The final stage; translates raw JSON data into a professional, scannable business narrative.

---

## 🚀 Deployment Guide

### 1. Local Development (Multi-Process Simulation)
To simulate microservices locally, use the provided execution script:

```bash
./run_local.sh
```
This launches 4 agents independently on ports 8000–8003. Access the **ADK Dev UI** at [http://localhost:8000](http://localhost:8000).

### 2. Cloud Production Deployment (Google Cloud Run)
For production, deploy each agent as a separate service on Google Cloud Run to enable scalable, independent agent communication.

#### A. Deploy Sub-Agents
Deploy these in parallel using `gcloud`:

```bash
# Deploy Researcher
gcloud run deploy researcher --source sap_analyst/Researcher/ --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI="true"

# Deploy Critic Validator
gcloud run deploy critic --source sap_analyst/critic_validator/ --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI="true"

# Deploy Story Teller
gcloud run deploy storyteller --source sap_analyst/Story_teller/ --region us-central1 --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI="true"
```

#### B. Capture Service URLs
Retrieve the assigned URLs after deployment:
```bash
RESEARCHER_URL=$(gcloud run services describe researcher --region us-central1 --format='value(status.url)')
CRITIC_URL=$(gcloud run services describe critic --region us-central1 --format='value(status.url)')
STORY_URL=$(gcloud run services describe storyteller --region us-central1 --format='value(status.url)')
```

#### C. Deploy Orchestrator
Configure the Orchestrator with the sub-agent URLs for A2A discovery:

```bash
gcloud run deploy orchestrator --source sap_analyst/orchestrator/ --region us-central1 --allow-unauthenticated \
  --set-env-vars RESEARCHER_AGENT_CARD_URL=$RESEARCHER_URL/a2a/agent/.well-known/agent-card.json \
  --set-env-vars CRITIC_AGENT_CARD_URL=$CRITIC_URL/a2a/agent/.well-known/agent-card.json \
  --set-env-vars STORY_AGENT_CARD_URL=$STORY_URL/a2a/agent/.well-known/agent-card.json \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI="true"
```

---

## 🛠 Project Structure

```text
SAP MVP/
├── .env                              # GCP configuration
├── requirements.txt                  # Project dependencies
├── run_local.sh                      # Local multi-process launch script
├── sap_analyst_sessions.db           # Persistent memory
└── sap_analyst/
    ├── orchestrator/                 # Root orchestrator & A2A config
    ├── Researcher/                   # SAP data tools & extraction logic
    ├── critic_validator/             # Data governance & auditing
    └── Story_teller/                 # Narrative generation
```

---

## 💾 Mock SAP Schema
The system uses in-memory dictionaries to mimic SAP HANA:
- **EKKO:** Purchasing Document Header
- **EKPO:** Purchasing Document Item
- **MARA:** General Material Data
- **MARD:** Storage Location Data

---

## 🎓 Thesis Context
This project addresses research in **Autonomous Multi-Agent Systems (MAS)**:
- **Autonomous Schema Navigation:** Agents discover relationships dynamically.
- **Data Governance:** Automated auditing via the Critic Validator.
- **Narrative Abstraction:** LLM-driven conversion of raw ERP data into business insights.
