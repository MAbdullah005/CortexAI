"""
Planner Node

Responsible for:
- Deciding what to do next
- Breaking tasks into steps
- Choosing when to call tools vs respond directly

This is the "brain" of your agent.
"""

from typing import Dict, Any

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
import json
import re

from app.llm.llm_config import llm
from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================
# Planner Prompt
# =========================================

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are an intelligent AI planner.

Your job:
1. Understand the user's request
2. Decide whether to:
   - Respond directly
   - Use a tool
   - Use multiple tools step-by-step

Available tools:
- calculator → math operations
- rag_tool → retrieve info from PDF
- search_tool → web search
- get_stock_price → stock data

Rules:
- If question is factual → use search_tool
- If question is from PDF → use rag_tool
- If math → use calculator
- If finance → use get_stock_price
- If simple → answer directly

Output STRICT JSON:

{
  "action": "tool" | "final",
  "tool_name": "tool_name_if_needed",
  "tool_input": "input_for_tool",
  "final_answer": "only if action is final"
}
"""),
    ("human", "{input}")
])


# =========================================
# Planner Logic
# =========================================



def extract_json(text: str):
    """
    Extract JSON from LLM response safely.
    """

    try:
        # Try direct parse first
        return json.loads(text)
    except:
        pass

    # Extract JSON inside ```json ... ```
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except:
            pass

    # Extract first {...}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    return None

def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decide next action for the agent.
    """

    try:
        messages = state.get("messages", [])
        print("Messages :",messages)
        user_input = messages[-1].content

        logger.info(f"Planner received input: {user_input}")

        # Run planner LLM
        response = llm.invoke(
            PLANNER_PROMPT.format_messages(input=user_input)
        )

        content = response.content

        logger.info(f"Planner raw output: {content}")

        # Try parsing JSON
        import json

        try:
            decision = extract_json(content)
            if decision is None:
               logger.warning("Planner output not valid JSON")
        except Exception:
            logger.warning("Planner output not valid JSON, fallback to final answer")

            return {
                "messages": [
                    AIMessage(content=content)
                ]
            }

        action = decision.get("action")

        # =================================
        # FINAL ANSWER
        # =================================
        if action == "final":
            return {
                "messages": [
                    AIMessage(content=decision.get("final_answer", ""))
                ]
            }

        # =================================
        # TOOL CALL
        # =================================
        elif action == "tool":

            tool_name = decision.get("tool_name")
            tool_input = decision.get("tool_input")

            logger.info(f"Planner chose tool: {tool_name}")

            return {
                "tool_call": {
                    "name": tool_name,
                    "input": tool_input
                }
            }

        else:
            logger.warning("Unknown planner action")

            return {
                "messages": [
                    AIMessage(content="I couldn't understand the request.")
                ]
            }

    except Exception as e:

        logger.error(f"Planner error: {str(e)}")

        return {
            "messages": [
                AIMessage(content="❌ Planner failed.")
            ]
        }