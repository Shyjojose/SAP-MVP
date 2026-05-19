import asyncio
import json
from pathlib import Path

from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
import importlib


AGENT_PORT_MAP = {
    "Researcher": 8001,
    "critic_validator": 8002,
    "Story_teller": 8003,
    "orchestrator": 8000,
}


async def build_and_write_card(agent_name: str, agents_dir: str):
    # Try importing as a package module under sap_analyst
    module_candidates = [
        f"sap_analyst.{agent_name}.agent",
        f"sap_analyst.{agent_name}",
        f"{agent_name}.agent",
        agent_name,
    ]
    module = None
    for m in module_candidates:
        try:
            module = importlib.import_module(m)
            break
        except Exception:
            continue

    if module is None:
        raise ImportError(f"Could not import module for agent {agent_name}")

    agent_or_app = getattr(module, "app", None) or getattr(module, "root_agent", None)
    if agent_or_app is None:
        raise RuntimeError(f"Module {module} has no 'app' or 'root_agent' attribute")

    agent = getattr(agent_or_app, "root_agent", agent_or_app)

    rpc_port = AGENT_PORT_MAP.get(agent_name, 8000)
    rpc_url = f"http://localhost:{rpc_port}/a2a/{agent_name}"

    builder = AgentCardBuilder(agent=agent, rpc_url=rpc_url)
    card = await builder.build()

    agent_dir = Path(agents_dir) / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)
    out_path = agent_dir / "agent.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(json.loads(card.json()), f, indent=2)
    print(f"Wrote agent card for {agent_name} to {out_path}")


def main():
    agents_dir = "sap_analyst"
    base = Path(agents_dir)
    agent_names = [p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith('.') and p.name != '__pycache__']
    loop = asyncio.get_event_loop()
    for name in agent_names:
        loop.run_until_complete(build_and_write_card(name, agents_dir))


if __name__ == "__main__":
    main()
