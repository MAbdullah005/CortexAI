import os
import sys
import uuid
import json
import streamlit as st
import requests

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Backend (KEEP — no delete as you requested)
from app.graph.agent_graph import chatbot
from app.core.ingest import ingest_pdf
from app.llm.llm_config import llm
from app.memory.thread_titles import set_thread_title
from app.core.retriever import thread_document_metadata
from app.memory.sqlite_memory import retrieve_all_threads
from app.memory.sqlite_memory import get_thread_title_db, save_thread_title
from app.memory.thread_titles import get_thread_title

from app.llm.title_generator import generate_chat_title


# =========================== Utilities ===========================

def generate_thread_id():
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []
    st.session_state["youtube_url"] = None   # ✅ ADD THIS

    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# =========================== API ===========================

API_URL = "http://localhost:8000/chat"
API_UPLOAD = "http://localhost:8000/upload-pdf"
API_SET_YT = "http://localhost:8000/set_youtube"
API_GET_YT = "http://localhost:8000/get_youtube"   # ✅ UPDATED


def call_api(user_input, thread_id):
    try:
        response = requests.post(
            API_URL,
            json={
                "message": user_input,
                "thread_id": thread_id
            }
        )
        return response.json().get("response", "⚠️ No response")
    except Exception as e:
        return f"❌ API Error: {str(e)}"


# ======================= Session Initialization ===================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

# Load YouTube URL from backend (per thread)
if "youtube_url" not in st.session_state:
    try:
        thread_key = st.session_state["thread_id"]
        res = requests.get(f"{API_GET_YT}/{thread_key}")
        if res.status_code == 200:
            st.session_state["youtube_url"] = res.json().get("youtube_url")
    except:
        st.session_state["youtube_url"] = None

thread_key = st.session_state["thread_id"]
threads = st.session_state["chat_threads"][::-1]
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})

selected_thread = None



# ============================ Sidebar ============================

st.sidebar.title("LangGraph Multi-Tool Chatbot")
st.sidebar.markdown(f"**Thread ID:** `{thread_key[:8]}`")

if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()

if st.sidebar.button("Clear Conversation"):
    st.session_state["message_history"] = []
    st.rerun()

st.sidebar.divider()

# ===================== PDF Upload =====================

uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_pdf:
    if uploaded_pdf.name not in thread_docs:

        with st.sidebar.status("Uploading & Indexing PDF..."):

            try:
                files = {"file": uploaded_pdf}
                data = {"thread_id": thread_key}

                res = requests.post(API_UPLOAD, files=files, data=data)  # ✅ UPDATED

                if res.status_code == 200:
                    thread_docs[uploaded_pdf.name] = {"status": "uploaded"}
                    st.sidebar.success("✅ PDF uploaded & indexed")
                else:
                    st.sidebar.error("❌ Upload failed")

            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")

    else:
        st.sidebar.info("PDF already indexed.")


# Show document info
if thread_docs:
    latest_doc = list(thread_docs.values())[-1]
    st.sidebar.success(
        f"{latest_doc.get('filename')} | "
        f"{latest_doc.get('chunks')} chunks | "
        f"{latest_doc.get('documents')} pages"
    )

st.sidebar.divider()

# ===================== YouTube Input =====================


st.sidebar.subheader("YouTube Video")

youtube_url = st.sidebar.text_input("Paste YouTube URL")

if st.sidebar.button("Load Video"):
    if youtube_url:
        try:
            res = requests.post(
                API_SET_YT,
                json={
                    "thread_id": thread_key,
                    "youtube_url": youtube_url
                }
            )

            if res.status_code == 200:
                st.session_state["youtube_url"] = youtube_url
                st.sidebar.success("✅ Video loaded successfully")
            else:
                st.sidebar.error("❌ Failed to load video")

        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")


# ===================== Past Conversations =====================

st.sidebar.subheader("Past Conversations")

for thread_id in threads:
    title = get_thread_title_db(thread_id)

    if st.sidebar.button(
        title
        ,key=f"thread-{thread_id}"):
           selected_thread = thread_id


# ============================ Main Chat ============================

st.title("Multi Utility Chatbot")

# Show messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask something...")


if user_input:

    current_title = get_thread_title_db(thread_key)

    if current_title.startswith("Chat"):
        try:
            new_title = generate_chat_title(user_input)
            save_thread_title(thread_key, new_title)
            st.rerun()
        except:
            pass

    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    # ===================== API CALL INSTEAD OF GRAPH =====================

    with st.chat_message("assistant"):

        ai_message = call_api(user_input, thread_key)   # ✅ UPDATED

        st.write(ai_message)

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    # ===================== Metadata (still works if needed) =====================

    doc_meta = thread_document_metadata(thread_key)
    if doc_meta:
        st.caption(
            f"Source: {doc_meta.get('filename')} | "
            f"Chunks: {doc_meta.get('chunks')} | "
            f"Pages: {doc_meta.get('documents')}"
        )



# ===================== YouTube Player =====================

if st.session_state.get("youtube_url"):
    st.video(st.session_state["youtube_url"])


# ============================ Thread Switch ============================

if selected_thread:
    st.session_state["thread_id"] = selected_thread

    # ✅ Load YouTube URL
    try:
        res = requests.get(f"{API_GET_YT}/{selected_thread}")
        if res.status_code == 200:
            st.session_state["youtube_url"] = res.json().get("youtube_url")
    except:
        st.session_state["youtube_url"] = None

    messages = load_conversation(selected_thread)

    temp_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_messages.append({"role": role, "content": msg.content})

    st.session_state["message_history"] = temp_messages
    st.rerun()


# ============================ Download Chat ============================

st.divider()

chat_json = json.dumps(st.session_state["message_history"], indent=2)

st.download_button(
    label="Download Chat History",
    data=chat_json,
    file_name="chat_history.json",
    mime="application/json",
)