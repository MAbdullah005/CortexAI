from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    thread_id: str


class ChatResponse(BaseModel):
    response: str
    thread_id: str


class ThreadResponse(BaseModel):
    thread_id: str
    title: str


class MessageSchema(BaseModel):
    role: str
    content: str