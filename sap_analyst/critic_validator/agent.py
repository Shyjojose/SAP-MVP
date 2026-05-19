from typing import Literal, List, Optional
from google.adk.agents import Agent
from google.adk.apps.app import App
from pydantic import BaseModel, Field


class critic(BaseModel):
    """Structured evaluation schema for the SAP Auditor / Validator Agent."""
    
    status: Literal["pass", "fail"] = Field(
        description="Whether the data/queries are accurate ('pass') or have flaws that require fixes ('fail')."
    )
    
    feedback: str = Field(
        description="Detailed technical reasoning. If 'fail', list what tables, keys, or data anomalies caused the rejection. If 'pass', provide a short audit confirmation."
    )
    
    detected_anomalies: Optional[List[str]] = Field(
        default=[],
        description="List of specific flaws found during audit (e.g., 'Broken Join between MARA and EKKO', 'Negative Price in NETPR'). Leave empty if status is 'pass'."
    )



critic_validator = Agent(
    name="critic_validator",
    model="gemini-2.5-flash",
    description="Strict SAP Data Governance Auditor that evaluates data accuracy.",
    tools=[], # No tools needed; it purely evaluates text/data inputs
    instruction="""You are a strict SAP Data Governance Auditor.
    You evaluate data provided by the Researcher against the original business goal.
    
    Your Validation Rules:
    1. Check for logical anomalies (e.g., negative prices in NETPR, invalid keys, broken joins).
    2. Ensure the returned data satisfies the original business question.
    
    Your Action Outputs:
    - If you find errors or flaws, respond explicitly with 'REJECTED' followed by a detailed, technical explanation of what the Researcher needs to fix.
    - If the logic is perfect and data makes sense, respond explicitly with 'APPROVED' followed by the valid data structured cleanly.
    """,
    
    output_schema=critic,
)

root_agent = critic_validator
