"""
wealthdesk/agent.py
-------------------
Graph construction and the terminal loop.

Run the agent from the repo root:
    cd cohort-1/wealthdesk/s01/starter
    python -m wealthdesk.agent

Session 1 graph:
    START --> respond --> END
"""
import sqlite3
from pathlib import Path
from uuid import uuid4

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from .nodes import respond
from .state import WealthDeskState

CHECKPOINT_DB = Path(__file__).parent.parent.parent.parent / "data" / "checkpoints.db"
CHECKPOINT_DB.parent.mkdir(parents=True, exist_ok=True)
# ---------------------------------------------------------------------------
# TODO 5 of 5 -- build_graph
# ---------------------------------------------------------------------------
# Implement build_graph() so it:
#
#   1. Creates a StateGraph:
#        builder = StateGraph(WealthDeskState)
#
#   2. Registers the respond node:
#        builder.add_node("respond", respond)
#
#   3. Sets the entry point (first node to run):
#        builder.set_entry_point("respond")
#
#   4. Connects respond → END (the graph exits after one response):
#        builder.add_edge("respond", END)
#
#   5. Compiles and returns the graph:
#        return builder.compile()
#
# ---------------------------------------------------------------------------

def build_graph(checkpointer=None):
    builder = StateGraph(WealthDeskState)
    builder.add_node("respond", respond)
    builder.set_entry_point("respond")
    builder.add_edge("respond", END)
    return builder.compile(checkpointer=checkpointer or MemorySaver())
# Module-level graph instance required by langgraph.json for LangGraph Studio.
# run() uses this directly rather than building a second copy.
graph = build_graph()


# ---------------------------------------------------------------------------
# Terminal loop (provided -- no changes needed)
# ---------------------------------------------------------------------------

def run() -> None:
    conn      = sqlite3.connect(str(CHECKPOINT_DB), check_same_thread=False)
    _graph    = build_graph(checkpointer=SqliteSaver(conn))
    thread_id = str(uuid4())
    config    = {"configurable": {"thread_id": thread_id}}
    print("=" * 55)
    print("  WealthDesk | Bharat National Bank")
    print("  Type 'quit' to exit")
    print("=" * 55)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nWealthDesk: Session ended. Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("\nWealthDesk: Thank you for choosing Bharat National Bank. Goodbye!")
            break

        result = _graph.invoke({"customer_message": user_input, "response": ""}, config=config)
        print(f"\nWealthDesk: {result['response']}")


if __name__ == "__main__":
    run()
