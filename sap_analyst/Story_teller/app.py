from google.adk.apps.app import App
from .agent import Story_teller

# ADK App definition for agent discovery and agent-card generation.
app = App(name="story_teller_app", root_agent=Story_teller, agents=[Story_teller])
