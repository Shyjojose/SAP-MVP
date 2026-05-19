from google.adk.apps.app import App
from .agent import Researcher

# ADK App definition for agent discovery and agent-card generation.
app = App(name="researcher_app", root_agent=Researcher, agents=[Researcher])
