"""
wealthdesk/nodes.py
-------------------
Node functions for the WealthDesk graph.

Each node is a plain Python function:
  - Input : the full WealthDeskState (read-only)
  - Output: a dict containing ONLY the keys this node changed
             (LangGraph merges it into the state automatically)
"""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .config import SYSTEM_PROMPT
from .state import WealthDeskState
from .tools import llm


BLOCKLIST = [
    "ignore all previous",
    "forget everything",
    "you are now",
    "disregard your system",
    "act as",
    "jailbreak",
]

def respond(state: WealthDeskState) -> dict:
    """Call the LLM and return the agent's reply."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    history = state.get("history", [])
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    messages.append(HumanMessage(content=state["customer_message"]))

    try:
        result = llm.invoke(messages)
        response_text = result.content
    except Exception as e:
        print(f"[WealthDesk] LLM error: {e}")
        return {"response": "I am temporarily unavailable. Please try again in a moment."}

    new_history = history + [
        {"role": "user", "content": state["customer_message"]},
        {"role": "assistant", "content": response_text},
    ]

    return {"response": response_text, "history": new_history}
