from __future__ import annotations

from app.utils.logger import get_logger
from typing import Annotated, Any, Dict, Optional, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage

logger = get_logger(__name__)
from langgraph.graph.message import add_messages



class ChatState(TypedDict):
    logger.info("Chat State inilize done")
    messages: Annotated[list[BaseMessage], add_messages]
