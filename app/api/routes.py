from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
import uuid
from fastapi import Form
from fastapi.responses import FileResponse
from app.services.youtube_loader import extract_video_id
from app.core.retriever import clear_thread_cache
import shutil
import os
import sqlite3
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
from app.services.youtube_ingest import ingest_youtube

from app.memory.sqlite_memory import save_youtube_url
from fastapi.responses import Response


from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Your existing backend imports
from app.graph.agent_graph import chatbot
from app.core.ingest import ingest_pdf
from app.memory.sqlite_memory import retrieve_all_threads, get_thread_title_db, save_thread_title
from app.memory.thread_titles import get_thread_title
from app.llm.title_generator import generate_chat_title
from langgraph.checkpoint.sqlite import SqliteSaver

router = APIRouter()

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chatbot_conv.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)


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
    thread_id = data["thread_id"]
    youtube_url = data["youtube_url"]

    from app.utils.hash_utils import hash_string

    video_id = extract_video_id(youtube_url)
    doc_hash = hash_string(video_id)

    cursor = conn.cursor()

    # 🔍 Check existing
    cursor.execute("SELECT doc_id FROM documents WHERE content_hash=?", (doc_hash,))
    row = cursor.fetchone()

    if row is not None:
        doc_id = row[0]
        print("....Video already parsent in vertor store ...")
        cursor.execute("""
        INSERT OR IGNORE INTO thread_documents (thread_id, doc_id)
        VALUES (?, ?)
        """,
        (thread_id, doc_id))
        conn.commit()
        clear_thread_cache(thread_id)

        return {"status": "reused", "Youtube_video_id": doc_id}
        
    else:
        import uuid
        doc_id = str(uuid.uuid4())

        # 🔥 Only fetch + embed ONCE
        vectorstore_path = ingest_youtube(video_id, doc_id)

        cursor.execute("""
        INSERT INTO documents (doc_id, type, content_hash, source, vectorstore_path)
        VALUES (?, ?, ?, ?, ?)
        """, (doc_id, "youtube", doc_hash, video_id, vectorstore_path))

    # 🔗 Link to thread
    cursor.execute("""
    INSERT OR IGNORE INTO thread_documents (thread_id, doc_id)
    VALUES (?, ?)
    """, (thread_id, doc_id))

    conn.commit()
    clear_thread_cache(thread_id)

    return {"status": "ok"}


@router.get("/get_youtube/{thread_id}")
def get_youtube(thread_id: str):
    cursor = conn.cursor()

    cursor.execute("""
    SELECT source FROM documents
    JOIN thread_documents USING(doc_id)
    WHERE thread_id=? AND type='youtube'
    """, (thread_id,))

    row = cursor.fetchone()

    if row:
        video_id = row[0]

        # Convert back to full URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        return {"youtube_url": youtube_url}

    return {"youtube_url": None}


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    thread_id: str = Form(...)
):
    content = await file.read()

    from app.utils.hash_utils import hash_bytes
    doc_hash = hash_bytes(content)

    cursor = conn.cursor()

    # 🔍 Check if document already exists
    cursor.execute("SELECT doc_id, vectorstore_path FROM documents WHERE content_hash=?", (doc_hash,))
    row = cursor.fetchone()

    if row:
        doc_id = row[0]

        # 🔗 Link to thread (NO RE-EMBEDDING)
        cursor.execute("""
        INSERT OR IGNORE INTO thread_documents (thread_id, doc_id)
        VALUES (?, ?)
        """, (thread_id, doc_id))

        conn.commit()
        clear_thread_cache(thread_id)

        return {"status": "reused", "doc_id": doc_id}

    # 🆕 New document
    import uuid
    doc_id = str(uuid.uuid4())

    file_path = os.path.join("data/uploads_pdfs/", f"{doc_hash}.pdf")

    with open(file_path, "wb") as f:
        f.write(content)
        

    # 🔥 INGEST ONLY ONCE
    vectorstore_path = ingest_pdf(
    file_bytes=content,
    filename=file.filename,
    doc_id=doc_id
)

    cursor.execute("""
    INSERT INTO documents (doc_id, type, content_hash, source, vectorstore_path)
    VALUES (?, ?, ?, ?, ?)
    """, (doc_id, "pdf", doc_hash, file_path, vectorstore_path))

    cursor.execute("""
    INSERT INTO thread_documents (thread_id, doc_id)
    VALUES (?, ?)
    """, (thread_id, doc_id))

    conn.commit()

    return {"status": "new", "doc_id": doc_id}

@router.get("/get_pdf/{thread_id}")
def get_pdf(thread_id: str):
    cursor = conn.cursor()

    cursor.execute("""
    SELECT source FROM documents
    JOIN thread_documents USING(doc_id)
    WHERE thread_id=? AND type='pdf'
    """, (thread_id,))

    row = cursor.fetchone()

    if row:
        file_path = row[0]

        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="application/pdf")

    return {"error": "No PDF found"}