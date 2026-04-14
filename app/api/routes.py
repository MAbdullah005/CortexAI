from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
import uuid

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Your existing backend imports
from app.graph.agent_graph import chatbot
from app.rag.ingest import ingest_pdf
from app.memory.sqlite_memory import retrieve_all_threads, get_thread_title_db, save_thread_title
from app.memory.thread_titles import get_thread_title
from app.llm.title_generator import generate_chat_title

router = APIRouter()


# ========================= Chat Endpoint =========================

@router.post("/chat")
async def chat_endpoint(data: dict):
    user_input = data["message"]
    thread_id = data["thread_id"]

    CONFIG = {
        "configurable": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
    )

    return {
        "response": response["messages"][-1].content
    }


# ========================= Upload PDF =========================

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), thread_id: str = ""):
    content = await file.read()

    summary = ingest_pdf(
        content,
        thread_id=thread_id,
        filename=file.filename,
    )

    return {"status": "success", "data": summary}


# ========================= Threads =========================

@router.get("/threads")
def get_threads():
    threads = retrieve_all_threads()
    result = []

    for t in threads:
        result.append({
            "thread_id": t,
            "title": get_thread_title_db(t)
        })

    return result


# ========================= New Thread =========================

@router.post("/new-thread")
def new_thread():
    thread_id = str(uuid.uuid4())
    save_thread_title(thread_id, "New Chat")
    return {"thread_id": thread_id}


# ========================= Get Conversation =========================

@router.get("/thread/{thread_id}")
def get_thread(thread_id: str):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    messages = state.values.get("messages", [])

    formatted = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        formatted.append({
            "role": role,
            "content": msg.content
        })

    return formatted


# ========================= Title Generation =========================

@router.post("/generate-title")
def generate_title(data: dict):
    thread_id = data["thread_id"]
    message = data["message"]

    title = generate_chat_title(message)
    save_thread_title(thread_id, title)

    return {"title": title}