# SAP Analyst MVP — Google ADK Multi-Agent System

An AI-powered SAP procurement analyst built with the **Google Agent Development Kit (ADK)** and **Vertex AI (Gemini 2.0 Flash)**. It uses a multi-agent pipeline to autonomously query SAP tables, validate data, and deliver business-ready supply chain insights — without requiring technical knowledge from the end user.

> This MVP serves as a proof-of-concept for the Master Thesis topic: **"Autonomous Generation of Multi-Agent Systems for Supply Chain Planning"** at SAP's Supply Chain Management (SCM) Data Science team.

---

## Architecture

```
User Query (natural language)
    │
    ▼
┌─────────────────────┐
│   sap_analyst       │  Root Orchestrator
│   (root agent)      │  Immediately delegates — never asks clarifying questions
└────────┬────────────┘
         │ transfer_to_agent
         ▼
┌─────────────────────┐
│  Critic_validator   │  Data Auditor
│  (sub-agent)        │  • Looks up table schemas (EKKO, EKPO, MARA, MARD)
│                     │  • Queries SAP tables via tools
│                     │  • Runs sanity checks (negatives, anomalies, joins)
│                     │  • Approves or rejects the data
└────────┬────────────┘
         │ transfer_to_agent
         ▼
┌─────────────────────┐
│   Story_teller      │  Business Narrator
│   (sub-agent)       │  • Translates validated data into plain-English narrative
│                     │  • Highlights key findings, risks, and recommended actions
└─────────────────────┘
```

---

## Project Structure

```
SAP MVP/
├── .env                              # GCP credentials (not committed)
├── .gitignore
├── requirements.txt
├── run.py                            # Starts ADK web server with persistent sessions
└── sap_analyst/
    ├── __init__.py
    ├── agent.py                      # Root agent (sap_analyst)
    ├── memory.py                     # Session memory tools (available, not wired by default)
    └── subagents/
        ├── Critic_validator/
        │   ├── agent.py              # Critic_validator agent
        │   └── tools.py             # query_sap_table, get_table_schema
        └── Story_teller/
            └── agent.py             # Story_teller agent
```

---

## Setup

### 1. Prerequisites
- Python 3.11+
- A GCP project with Vertex AI API enabled
- `gcloud` CLI authenticated (`gcloud auth application-default login`)

### 2. Clone and install

```bash
git clone <repo-url>
cd "SAP MVP"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
GOOGLE_GENAI_USE_VERTEXAI="true"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
```

### 4. Run the ADK Dev UI

```bash
python3 run.py
```

Open **http://127.0.0.1:8000** in your browser.

---

## Mock Schema — How It Mimics SAP HANA

The system simulates a real SAP ERP database using in-memory Python dictionaries in `sap_analyst/subagents/Critic_validator/tools.py`. Each mock table mirrors the exact field names, data types, and relationships of its real SAP counterpart — allowing the agents to reason about the schema exactly as they would in production.

### How the mock works

```
tools.py
  ├── get_table_schema(table_name)   → returns field names + descriptions (mimics SE11 / Data Dictionary)
  └── query_sap_table(table_name, filters) → returns rows + columns (mimics SELECT from SAP HANA / BigQuery)
```

The `Critic_validator` agent calls these tools autonomously — it does not receive pre-written SQL. It reads the schema, decides which tables to join, queries them, then cross-checks the results for business logic errors.

### Mock Tables

#### EKKO — Purchasing Document Header
Mirrors the SAP table that stores one row per Purchase Order.

| Field | Type | Description |
|-------|------|-------------|
| EBELN | String | Purchase Order Number (key) |
| LIFNR | String | Vendor Account Number |
| BEDAT | Date | Purchase Order Date |
| WAERS | String | Currency Key (USD, EUR, etc.) |

**Mock data:** 3 purchase orders across 2 vendors in USD and EUR.

#### EKPO — Purchasing Document Item
Mirrors the SAP table that stores line items for each Purchase Order (one PO can have many items).

| Field | Type | Description |
|-------|------|-------------|
| EBELN | String | Purchase Order Number (FK → EKKO) |
| EBELP | String | Item Number within PO |
| MATNR | String | Material Number (FK → MARA) |
| MENGE | Float | Ordered Quantity |
| NETPR | Float | Net Price per Unit |

**Mock data:** 3 line items with realistic quantities and prices.

#### MARA — General Material Data
Mirrors the SAP material master table — the central record for every product.

| Field | Type | Description |
|-------|------|-------------|
| MATNR | String | Material Number (key) |
| MAKTX | String | Material Description |
| MEINS | String | Base Unit of Measure (EA, KG, etc.) |
| MTART | String | Material Type (FERT=Finished, ROH=Raw Material) |

**Mock data:** 3 materials — Pump Assembly XL (finished good), Steel Rod 10mm (raw), Hydraulic Valve (finished good).

#### MARD — Storage Location Data
Mirrors the SAP table that tracks stock levels per plant and storage location.

| Field | Type | Description |
|-------|------|-------------|
| MATNR | String | Material Number (FK → MARA) |
| WERKS | String | Plant Code |
| LGORT | String | Storage Location |
| LABST | Float | Unrestricted-Use Stock Quantity |

**Mock data:** Stock levels across 2 storage locations at plant 1000.

### Relationship Model

```
EKKO (PO Header)
  └── EKPO (PO Items)  ←── MATNR ──► MARA (Material Master)
                                           │
                                           └── MATNR ──► MARD (Stock Levels)
```

This mirrors real SAP procurement joins: you start with the PO header, expand to line items, then enrich with material descriptions and check current stock.

### Replacing Mock Data with Real SAP / BigQuery

To connect to a real SAP HANA or BigQuery backend, replace the dictionary lookups in `tools.py` with:

```python
from google.cloud import bigquery

client = bigquery.Client()

def query_sap_table(table_name: str, filters: dict = None) -> dict:
    query = f"SELECT * FROM `your-project.sap_dataset.{table_name}`"
    # add WHERE clauses from filters
    result = client.query(query).result()
    return {"columns": [...], "rows": [...]}
```

No changes to agents or prompts are needed — the tool interface stays identical.

---

## Example Query

**User:** *"Give me a full picture of our open purchase orders, vendors, spend and risks."*

**Agent pipeline:**
1. `sap_analyst` → immediately transfers to `Critic_validator`
2. `Critic_validator` → checks schemas → queries EKKO + EKPO + MARA → validates → transfers to `Story_teller`
3. `Story_teller` → produces business narrative

**Sample Output:**
```
Headline: Open purchase orders show a total commitment of $2,500 USD and €750 EUR.

Key Findings:
• PO 4500000001 — 10x Pump Assembly XL from VENDOR_001 @ $250/ea = $2,500
• PO 4500000002 — 500 KG Steel Rod 10mm from VENDOR_002 @ €1.5/KG = €750

Anomalies & Risks:
• Large quantity (500 KG) for Steel Rod — verify demand aligns with forecast.

Recommended Actions:
• Confirm Steel Rod demand with production planning.
• Explore volume discounts with both vendors.
```

---

## Thesis Context — SAP SCM Data Science

This project directly addresses the research gaps identified in the SAP Master Thesis:

> *"Autonomous multi-agent systems (MAS) that dynamically generate agentic workflows, assign specialized roles to agents, facilitate collaborative work, and continuously improve their processes represent the cutting edge of agentic system research. However, while autonomous MAS show promise for complex analytical tasks, their effectiveness in enterprise supply chain environments remains largely unexplored."*

### What This MVP Demonstrates

| Thesis Requirement | How This MVP Addresses It |
|---|---|
| Autonomous multi-step SAP schema navigation | `Critic_validator` autonomously discovers table relationships without pre-written SQL |
| Abstraction of technical complexity from end users | Users query in plain English; agents handle all SAP field codes internally |
| Intelligent diagnostic support for planning outputs | `Story_teller` translates raw data into actionable procurement insights |
| Multi-agent role specialisation | Validator and Narrator roles are cleanly separated with explicit handoff protocol |
| Evaluation of agentic systems in enterprise SCM | Full ADK Dev UI trace allows evaluation of reasoning steps, tool calls, and outputs |

---

## Future Improvements (Thesis Roadmap)

### 1. Benchmark Development
The thesis calls for a **curated dataset of progressively complex supply chain scenarios** requiring multi-step SQL queries.

- Expand mock schema to include full SAP SCM tables: `PLAF` (planned orders), `MD04` (stock/requirements list), `LIPS` (delivery items), `VBAP` (sales order items), `MB51` (material movements)
- Build a benchmark suite of 50–100 natural language questions mapped to ground-truth SQL and expected output — ranging from simple single-table lookups to complex multi-table aggregations
- Use existing open-source datasets (e.g., Supply Chain datasets on Kaggle, or SAP's own demo IDES data) as the basis for realistic mock data

### 2. Autonomous Workflow Generation
Currently the pipeline is fixed (Critic_validator → Story_teller). A key thesis contribution would be **dynamic agent generation**:

- The root agent analyses the user query and spawns a workflow of specialised sub-agents on demand (e.g., adding a `Demand_Forecaster` or `Inventory_Checker` agent when needed)
- Use `LoopAgent` or `SequentialAgent` from ADK to enable iterative refinement loops where the validator can trigger a re-query cycle
- Explore `LangGraph`-style conditional edges for branching workflows based on data quality signals

### 3. RAG-Grounded Schema Expert
Replace the hardcoded `get_table_schema` tool with **Vertex AI Search (RAG)**:

- Index the full SAP Data Dictionary (field descriptions, table relationships, business rules) as a Vertex AI Search corpus
- The `Critic_validator` retrieves relevant schema context dynamically — enabling it to handle any SAP table, not just the four mocked here
- This directly addresses the thesis requirement for *"sophisticated SAP schema navigation"*

### 4. System Validation & Evaluation
The thesis requires **assessing system accuracy and reliability**:

- Implement an automated evaluation harness: run each benchmark query, compare agent-generated SQL to ground truth, score accuracy and hallucination rate
- Use the ADK's built-in eval framework (`adk eval`) with custom scorers for SAP-specific correctness
- Track metrics: schema accuracy, query correctness, narrative quality (using LLM-as-judge), and end-to-end latency
- Introduce a `Model_Monitor` agent that flags when the system produces outputs inconsistent with historical patterns (Vertex AI Model Monitoring)

### 5. A2A Protocol & Cross-Framework Agents
Implement the **Agent-to-Agent (A2A) protocol** (2026 standard):

- Expose the `Critic_validator` as an A2A-compliant service with an Agent Card
- Allow external agents (e.g., a Python-based demand planning agent or a SAP BTP agent) to call into this system securely
- This enables true enterprise interoperability across SAP's technology stack

### 6. Production Deployment
- Deploy to **Vertex AI Agent Engine** for managed scaling and "Memory Banks"
- Connect to real **SAP HANA via BigQuery** (SAP Datasphere integration)
- Add **LFA1/LFB1** vendor master, **VBAK/VBAP** sales orders, and **MD04** MRP tables
- Enable persistent long-term memory using Agent Engine's built-in session management

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Google ADK 1.26.0 |
| LLM | Gemini 2.0 Flash (Vertex AI) |
| Session Storage | SQLite via aiosqlite |
| Web Server | Uvicorn + FastAPI |
| GCP Services | Vertex AI, Cloud Project |
| Future: Real DB | BigQuery + SAP Datasphere |
| Future: Memory | Vertex AI Agent Engine |
| Future: RAG | Vertex AI Search |
