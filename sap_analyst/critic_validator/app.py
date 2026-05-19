from google.adk.apps.app import App
from .agent import critic_validator

# ADK App definition for agent discovery and agent-card generation.
app = App(name="critic_validator_app", root_agent=critic_validator, agents=[critic_validator])
