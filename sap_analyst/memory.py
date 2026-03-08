"""
Session state and memory tools for the SAP Analyst agent.

- save_insight:    Saves a key finding to session state (persists within session).
- get_session_memory: Retrieves all saved insights from the current session.
- search_past_sessions: Searches long-term memory across past sessions.
"""

from datetime import datetime, timezone

from google.adk.tools import FunctionTool, ToolContext


def save_insight(
    insight: str,
    category: str,
    tool_context: ToolContext,
) -> dict:
    """
    Save a key insight or finding to session memory.

    Args:
        insight: The finding to remember (e.g., 'PO 4500000002 has 500 units from VENDOR_002 — unusually high').
        category: Category tag for the insight. One of: 'anomaly', 'query', 'vendor', 'material', 'recommendation'.
        tool_context: ADK context (injected automatically).

    Returns:
        Confirmation with the saved entry.
    """
    insights: list = tool_context.state.get("insights", [])
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "insight": insight,
    }
    insights.append(entry)
    tool_context.state["insights"] = insights
    tool_context.state["last_updated"] = entry["timestamp"]
    return {"status": "saved", "entry": entry, "total_insights": len(insights)}


def get_session_memory(tool_context: ToolContext) -> dict:
    """
    Retrieve all insights saved in the current session.

    Args:
        tool_context: ADK context (injected automatically).

    Returns:
        All saved insights grouped by category.
    """
    insights: list = tool_context.state.get("insights", [])
    if not insights:
        return {"status": "empty", "message": "No insights saved in this session yet."}

    grouped: dict = {}
    for entry in insights:
        cat = entry.get("category", "general")
        grouped.setdefault(cat, []).append(entry["insight"])

    return {
        "status": "ok",
        "session_start": tool_context.state.get("session_start", "unknown"),
        "last_updated": tool_context.state.get("last_updated"),
        "total_insights": len(insights),
        "insights_by_category": grouped,
    }


async def search_past_sessions(query: str, tool_context: ToolContext) -> dict:
    """
    Search long-term memory across all past sessions for relevant SAP insights.

    Args:
        query: Natural language search query (e.g., 'anomalies in VENDOR_001 orders').
        tool_context: ADK context (injected automatically).

    Returns:
        Relevant memories from past sessions.
    """
    results = await tool_context.search_memory(query)
    memories = []
    for mem in results.memories:
        for event in mem.events:
            for part in event.content.parts:
                if part.text:
                    memories.append(part.text)

    if not memories:
        return {"status": "empty", "message": f"No past memories found for: '{query}'"}

    return {
        "status": "ok",
        "query": query,
        "results_count": len(memories),
        "memories": memories,
    }


save_insight_tool = FunctionTool(save_insight)
get_session_memory_tool = FunctionTool(get_session_memory)
search_past_sessions_tool = FunctionTool(search_past_sessions)
