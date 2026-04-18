from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
import uuid
from fastapi import Form
from fastapi.responses import FileResponse
import shutil
import os
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse

from app.memory.sqlite_memory import save_youtube_url
from fastapi.responses import Response


from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Your existing backend imports
from app.graph.agent_graph import chatbot
from app.core.ingest import ingest_pdf
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


@router.post("/set_youtube")
def set_youtube(data: dict):
    thread_id = data.get("thread_id")
    youtube_url = data.get("youtube_url")

    if not thread_id or not youtube_url:
        return {"error": "thread_id and youtube_url are required"}

    # ✅ Save in DB
    save_youtube_url(thread_id, youtube_url)

    # ✅ Reset in-memory retriever cache (IMPORTANT)
    try:
        from app.core.thread_store import _THREAD_DATA

        if thread_id in _THREAD_DATA:
            _THREAD_DATA[thread_id]["youtube_retriever"] = None

    except Exception:
        pass  # safe fallback if not using cache

    return {"status": "YouTube URL saved successfully"}

@router.get("/get_youtube/{thread_id}")
def get_youtube(thread_id: str):
    from app.memory.sqlite_memory import get_youtube_url

    url = get_youtube_url(thread_id)

    return {"youtube_url": url}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    thread_id: str = Form(...)   # 🔥 IMPORTANT FIX
):
    print("🔥 UPLOAD ENDPOINT HIT 🔥")

    if not thread_id:
        return {"error": "thread_id missing"}

    file_path = os.path.join(UPLOAD_DIR, f"{thread_id}.pdf")

    print("THREAD ID:", thread_id)
    print("SAVE PATH:", file_path)

    content = await file.read()

    if not content:
        return {"error": "File is empty"}

    with open(file_path, "wb") as f:
        f.write(content)

    print("EXISTS AFTER SAVE:", os.path.exists(file_path))

    summary = ingest_pdf(
        content,
        thread_id=thread_id,
        filename=file.filename,
    )

    return {"status": "success", "data": summary}


@router.get("/get_pdf/{thread_id}")
def get_pdf(thread_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{thread_id}.pdf")

    print("GET FILE PATH:", file_path)
    print("EXISTS:", os.path.exists(file_path))
    cwd = os.getcwd()
    print(cwd)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf")

    return {"error": "No PDF found"}