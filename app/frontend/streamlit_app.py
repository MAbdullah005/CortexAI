import os
import sys
import uuid
import json
import streamlit as st

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Backend
from app.graph.agent_graph import chatbot
from app.rag.ingest import ingest_pdf
from app.llm.llm_config import llm
from app.memory.thread_titles import set_thread_title
from app.rag.retriever import thread_document_metadata
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
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# ======================= Session Initialization ===================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

thread_key = st.session_state["thread_id"]
threads = st.session_state["chat_threads"][::-1]
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})

selected_thread = None


# ============================ Sidebar ============================

st.sidebar.title("LangGraph Multi-Tool Chatbot")
st.sidebar.markdown(f"**Thread ID:** `{thread_key[:8]}`")
st.sidebar.write("Titles:", st.session_state.get("thread_titles", {}))
#.....
st.sidebar.write(st.session_state.get("thread_titles", {}))
#....

if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()

if st.sidebar.button("Clear Conversation"):
    st.session_state["message_history"] = []
    st.rerun()



st.sidebar.divider()

# PDF Upload
uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name not in thread_docs:
        with st.sidebar.status("Indexing PDF..."):
            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )
            thread_docs[uploaded_pdf.name] = summary
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


# Past Conversations
st.sidebar.subheader("Past Conversations")

for thread_id in threads:
    title = get_thread_title_db(thread_id)

    if st.sidebar.button(
        title,
        key=f"thread-{thread_id}"
    ):
        
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
          st.rerun()  # IMPORTANT
      except:
          pass


    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {
        "configurable": {"thread_id": thread_key},
        "run_name": "chat_turn",
    }



    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_stream():
            for event in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                message_chunk = event[0]

                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"Using tool: {tool_name}", expanded=True
                        )
                    st.code(message_chunk.content)

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_stream())

        

        if status_holder["box"]:
            status_holder["box"].update(label="Tool finished", state="complete")

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    # Show document metadata
    doc_meta = thread_document_metadata(thread_key)
    if doc_meta:
        st.caption(
            f"Source: {doc_meta.get('filename')} | "
            f"Chunks: {doc_meta.get('chunks')} | "
            f"Pages: {doc_meta.get('documents')}"
        )


# ============================ Thread Switch ============================

if selected_thread:
    st.session_state["thread_id"] = selected_thread
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