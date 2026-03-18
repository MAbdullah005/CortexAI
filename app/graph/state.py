from __future__ import annotations

from app.utils.logger import get_logger
from typing import Annotated, Any, TypedDict,List,Dict
from langchain_core.messages import BaseMessage

logger = get_logger(__name__)
from langgraph.graph.message import add_messages



class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    tool_call: Dict[str, Any]
