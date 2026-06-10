import os
import sys
import uuid
import json
import streamlit as st
import requests
# video url 1 :https://www.youtube.com/watch?v=uvsp0zKhPV4
# video url 2 :https://www.youtube.com/watch?v=kwd8rwkuoWc

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain_core.messages import HumanMessage

# Backend imports (kept as requested — no deletions)
from app.graph.agent_graph import chatbot
from app.core.retriever import thread_document_metadata
from app.memory.sqlite_memory import retrieve_all_threads
from app.memory.sqlite_memory import get_thread_title_db, save_thread_title


# =========================== GLOBAL UI STYLE ===========================
st.markdown("""
<style>
.block-container { padding: 0rem !important; }
.main > div { gap: 0rem !important; }
section[data-testid="stSidebar"] { width: 240px !important; }
div[data-testid="column"] { padding: 0px !important; }
.chat-box { height: 80vh; overflow-y: auto; }
.video-box { height: 90vh; overflow-y: auto; padding: 0px; margin: 0px; }
.element-container { margin-bottom: 0px !important; }
</style>
""", unsafe_allow_html=True)


# =========================== Utilities ===========================

def generate_thread_id():
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []
    st.session_state["youtube_url"] = None
    st.session_state["pdf_uploaded"] = False      # ← ADD THIS
    st.session_state["ingested_docs"][thread_id] = {}  # ← ADD THIS
    save_thread_title(thread_id, "New Chat")
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# =========================== API ===========================

API_URL = "http://localhost:8000/chat"
API_UPLOAD = "http://localhost:8000/upload-pdf"
API_GET_PDF = "http://localhost:8000/get_pdf"
API_SET_YT = "http://localhost:8000/set_youtube"
API_GET_YT = "http://localhost:8000/get_youtube"
API_GEN_TITLE = "http://localhost:8000/generate-title"


def call_api(user_input, thread_id):
    try:
        response = requests.post(
            API_URL,
            json={"message": user_input, "thread_id": thread_id}
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

if "pdf_uploaded" not in st.session_state:
    st.session_state["pdf_uploaded"] = False

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

uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
if uploaded_pdf:
    # FIX: Key check was "uploaded" but the dict stores by filename — so the
    # guard never triggered and every Streamlit rerun re-uploaded the file.
    # Now keyed by filename, which is what's actually stored below.
    if uploaded_pdf.name not in thread_docs:
        print("Here is Upload PDF Name ",uploaded_pdf.name)
        with st.sidebar.status("Uploading & Indexing PDF..."):
            try:
                files = {
                    "file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")
                }
                data = {"thread_id": thread_key}

                res = requests.post(API_UPLOAD, files=files, data=data)

                if res.status_code == 200:
                    thread_docs[uploaded_pdf.name] = {
                        "status": "uploaded",
                        "filename": uploaded_pdf.name,
                    }
                    st.session_state["pdf_uploaded"] = True
                    st.sidebar.success("✅ PDF uploaded & indexed")
                else:
                    st.sidebar.error("❌ Upload failed")

            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    else:
        print("Here is Upload PDF Name  Already Uploaded",uploaded_pdf.name)
        st.sidebar.info("PDF already indexed.")

if thread_docs:
    latest_doc = list(thread_docs.values())[-1]
    # FIX: "chunks" and "documents" keys were never set in the dict above —
    # only "status" and "filename" were stored, so the sidebar always showed
    # "None chunks | None pages". Removed the missing keys; show only what
    # we actually have.
    st.sidebar.success(f"📄 {latest_doc.get('filename')} — uploaded")

st.sidebar.divider()

st.sidebar.subheader("YouTube Video")

youtube_url = st.sidebar.text_input("Paste YouTube URL")

if st.sidebar.button("Load Video"):
    if youtube_url:
        try:
            res = requests.post(
                API_SET_YT,
                json={"thread_id": thread_key, "youtube_url": youtube_url}
            )
            if res.status_code == 200:
                st.session_state["youtube_url"] = youtube_url
                st.sidebar.success("✅ Video loaded successfully")
            else:
                st.sidebar.error("❌ Failed to load video")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")

st.sidebar.subheader("Past Conversations")

for thread_id in threads:
    title = get_thread_title_db(thread_id)
    if st.sidebar.button(title, key=f"thread-{thread_id}"):
        selected_thread = thread_id


# ============================ MAIN LAYOUT ============================

st.title("Multi Utility Chatbot")

split_ratio = st.slider("Resize Chat ↔ Video", 10, 60, 70)

col_video, col_chat = st.columns([100 - split_ratio, split_ratio], gap="small")


# ============================ CHAT ============================
with col_chat:
    st.subheader("💬 Chat")

    chat_container = st.container()

    with chat_container:
        for message in st.session_state["message_history"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    user_input = st.chat_input("Ask something...")

    if user_input:
        st.session_state["message_history"].append(
            {"role": "user", "content": user_input}
        )
        st.session_state["message_history"].append(
            {"role": "assistant", "content": "⏳ Thinking..."}
        )
        st.rerun()

    if st.session_state["message_history"]:
        last_msg = st.session_state["message_history"][-1]

        if last_msg["role"] == "assistant" and last_msg["content"] == "⏳ Thinking...":
            user_msg = st.session_state["message_history"][-2]["content"]
            print("....Usear Message ....:", user_msg)
            ai_message = call_api(user_msg, thread_key)
            st.session_state["message_history"][-1]["content"] = ai_message

            # FIX: Generate and save title after the FIRST exchange only,
            # so the sidebar shows a meaningful name instead of "New Chat".
            if len(st.session_state["message_history"]) == 2:
                try:
                    requests.post(
                        API_GEN_TITLE,
                        json={"thread_id": thread_key, "message": user_msg}
                    )
                except Exception:
                    pass

            st.rerun()

        # FIX: thread_id was an undefined variable here — the loop variable
        # from the sidebar `for thread_id in threads` had leaked into this
        # scope and pointed to the LAST past thread, not the current one.
        # Changed to thread_key which is always the active thread.
        doc_meta = thread_document_metadata(thread_key)
        if doc_meta:
            for src in doc_meta["sources"]:
                st.caption(f"{src['type'].upper()}: {src['name']}")


# ============================ VIDEO + PDF ============================
with col_video:
    st.subheader("🎥 Video + 📄 Document")

    st.markdown('<div class="video-box">', unsafe_allow_html=True)

    if st.session_state.get("youtube_url"):
        st.video(st.session_state["youtube_url"])
    else:
        st.info("No video loaded")

    st.markdown("<div style='margin-top:5px'></div>", unsafe_allow_html=True)

    if st.session_state.get("pdf_uploaded"):
        pdf_url = f"{API_GET_PDF}/{thread_key}"
        pdf_html = f"""
        <iframe 
            src="{pdf_url}" 
            width="100%" 
            height="600px"
            style="border:none;">
        </iframe>
        """
        st.markdown(pdf_html, unsafe_allow_html=True)
    else:
        st.info("Upload a PDF to view it here")

    st.markdown('</div>', unsafe_allow_html=True)


# ============================ Thread Switch ============================

if selected_thread:
    st.session_state["thread_id"] = selected_thread
    st.session_state["pdf_uploaded"] = False

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


# ============================ Download ============================

st.divider()

chat_json = json.dumps(st.session_state["message_history"], indent=2)

st.download_button(
    label="Download Chat History",
    data=chat_json,
    file_name="chat_history.json",
    mime="application/json",
)