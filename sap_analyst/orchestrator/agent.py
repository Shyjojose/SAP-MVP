import os
import json
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from sap_analyst.orchestrator.authenticated_httpx import create_authenticated_client

def create_save_output_callback(key: str):
    """ every time analyst and critic chat it is saved in session state """
    def callback(callback_context: CallbackContext, **kwargs) -> None:
        ctx = callback_context

        for event in reversed(ctx.session.events):
            # here the agent checking session in reverse oder to find the latest message from itself and save the content in session state
            if event.author == ctx.agent_name and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    if key == "critic" and text.strip().startswith("{"):
                        try:
                            ctx.state[key] = json.loads(text)
                        except json.JSONDecodeError:
                            ctx.state[key] = text # if json decoding fails, save the raw text for debugging
                        else:
                            ctx.state[key] = text
                        print(f"[{ctx.agent_name}] Saved output to state['{key}']")
                        return
                    
    return callback

# connecting researcher ,critic_validator and story teller together using RemoteA2aAgent to call each other via A2A protocol and save the output in session state for next agent to use

researcher_url = os.environ.get(
    "RESEARCHER_AGENT_CARD_URL",
    "http://localhost:8001/a2a/Researcher/.well-known/agent-card.json",
)
researcher = RemoteA2aAgent(
    name="researcher",
    agent_card=researcher_url,
    description="Gathers information using Google Search.",
    # IMPORTANT: Save the output to state for the Judge to see
    after_agent_callback=create_save_output_callback("research_findings"),
    # IMPORTANT: Use authenticated client for communication
    httpx_client=create_authenticated_client(researcher_url)
)

critic_validator_url = os.environ.get(
    "JUDGE_AGENT_CARD_URL",
    os.environ.get(
        "CRITIC_VALIDATOR_AGENT_CARD_URL",
        "http://localhost:8002/a2a/critic_validator/.well-known/agent-card.json",
    ),
)
critic_validator = RemoteA2aAgent(
    name="critic_validator",
    agent_card=critic_validator_url,
    description="Evaluates the Researcher's findings for accuracy and relevance.",
    # IMPORTANT: Save the output to state for the Story Teller to see
    after_agent_callback=create_save_output_callback("critic"),
    # IMPORTANT: Use authenticated client for communication
    httpx_client=create_authenticated_client(critic_validator_url)
)

story_teller_url = os.environ.get(
    "CONTENT_BUILDER_AGENT_CARD_URL",
    os.environ.get(
        "STORY_TELLER_AGENT_CARD_URL",
        "http://localhost:8003/a2a/Story_teller/.well-known/agent-card.json",
    ),
)
story_teller = RemoteA2aAgent(
    name="story_teller",
    agent_card=story_teller_url,   
    description="Translates validated findings into a business narrative.",
    # IMPORTANT: Use authenticated client for communication
    httpx_client=create_authenticated_client(story_teller_url)
)

#escalation checker it should check if critic_validator reject the researcher's output and if status is pass it should break the loop

class EscalationChecker(BaseAgent):
    """Checks if the critic_validator has approved the researcher's findings. If not, it triggers a re-run of the Researcher agent."""

    async def _run_async_impl(self, ctx: InvocationContext)-> AsyncGenerator[Event, None]:
        feedback= ctx.session.state.get("critic")
        print(f"[EscalationChecker] Retrieved critic output from state: {feedback}")

        #check for status pass

        is_pass = False
        if isinstance(feedback, dict) and feedback.get("status") == "pass":
            is_pass = True
        # Handle string fallback if JSON parsing failed
        elif isinstance(feedback, str) and '"status": "pass"' in feedback:
            is_pass = True

        if is_pass:
            # 'escalate=True' tells the parent LoopAgent to stop looping
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # Continue the loop
            yield Event(author=self.name)       

escalation_checker = EscalationChecker(name="escalation_checker")

#defining the loop agent to cycle through the researcher,escalation_checker and critic_validator until the critic_validator approves the researcher's output

research_loop = LoopAgent(
    name="research_loop",
    sub_agents=[researcher, critic_validator, escalation_checker],
    description="iteratively research and critique until the critic approves the researcher's findings.",
    max_iterations=3,  # Prevent infinite loops
)

root_agent = SequentialAgent(
    name="root_agent",
    sub_agents=[research_loop, story_teller],
    description="A pipeline that researches a topic and tells bussiness story based on the research findings. It loops between Researcher and Critic Validator until the findings are approved, then passes the approved findings to the Story Teller for narrative generation."
)   