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

# =========================== API ===========================

API_URL = "http://localhost:8000/chat"
API_UPLOAD = "http://localhost:8000/upload-pdf"
API_GET_PDF = "http://localhost:8000/get_pdf/{thread_id}"
API_SET_YT = "http://localhost:8000/set_youtube"
API_GET_YT = "http://localhost:8000/get_youtube/{thread_id}"
API_GEN_TITLE = "http://localhost:8000/generate-title"
API_NEW_THREAD = "http://localhost:8000/new-thread"
#API_REtrived_all_thread="http://localhost:8000//retrived-all-thread"
#API_GET_THREAD_TITLE_DB="http://localhost:8000//get-thread-title"
#API_SET_THREAD_TITLE="http://localhost:8000//save-thread-title"

API_THREADS = "http://localhost:8000/threads"

API_THREAD_DETAILS = "http://localhost:8000/thread/{thread_id}/details"

API_THREAD_DOCS = "http://localhost:8000/thread/{thread_id}/documents"

API_THREAD_SOURCES = "http://localhost:8000/thread/{thread_id}/sources"




# =========================== Utilities ===========================


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

if "youtube_url" not in st.session_state:
    st.session_state["youtube_url"] = None

if "thread_id" not in st.session_state:
    response = requests.post(API_NEW_THREAD)
    st.session_state["thread_id"] = response.json()["thread_id"]


if "pdf_uploaded" not in st.session_state:
    st.session_state["pdf_uploaded"] = False

if "youtube_loaded_for" not in st.session_state:
    st.session_state["youtube_loaded_for"] = None

if "sources" not in st.session_state:
    st.session_state["sources"] = {}

if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None


thread_key = st.session_state["thread_id"]


selected_thread = None



# ============================ Sidebar ============================

st.sidebar.title("LangGraph Multi-Tool Chatbot")
st.sidebar.markdown(f"**Thread ID:** `{thread_key[:8]}`")

if st.sidebar.button("New Chat"):

    response = requests.post(API_NEW_THREAD)
    st.session_state["youtube_url"] = None
    st.session_state["pdf_uploaded"] = False

    st.session_state["thread_id"] = (
        response.json()["thread_id"]
    )

    st.session_state["message_history"] = []

    st.rerun()



if st.sidebar.button("Clear Conversation"):
    st.session_state["message_history"] = []
    st.rerun()

st.sidebar.divider()

uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name != st.session_state["uploaded_file_name"]:

        files = {
         "file": (
             uploaded_pdf.name,
             uploaded_pdf.getvalue(),
             "data/pdf\vectorstores"
              )
            }

        data = {
         "thread_id": st.session_state["thread_id"]
        }

        res = requests.post(
        API_UPLOAD,
        files=files,
        data=data
    )
        
        if res.status_code == 200:
          st.session_state["pdf_uploaded"] = True
    st.session_state["uploaded_file_name"] = uploaded_pdf.name

    


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

threads = requests.get(API_THREADS).json()

for thread in threads:

    if st.sidebar.button(
        thread["title"],
        key=thread["thread_id"]
    ):
        selected_thread = thread["thread_id"]


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
        print("message history before rerun first time ",st.session_state["message_history"])
        st.rerun()

    if st.session_state["message_history"]:
        last_msg = st.session_state["message_history"][-1]

        if last_msg["role"] == "assistant" and last_msg["content"] == "⏳ Thinking...":
            user_msg = st.session_state["message_history"][-2]["content"]
            print("....Usear Message ....:", user_msg)
            ai_message = call_api(user_msg, thread_key)
            st.session_state["message_history"][-1]["content"] = ai_message
            print("message history before rerun second  time ",st.session_state["message_history"])


            
            if len(st.session_state["message_history"]) == 2:
                try:
                    res_title=requests.post(
                        API_GEN_TITLE,
                        json={"thread_id": thread_key, "message": user_msg}
                    )
                        
                except Exception:
                    pass


            st.rerun()

        


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
        pdf_url = API_GET_PDF.format(
    thread_id=thread_key
)
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

    details = requests.get(
        f"http://localhost:8000/thread/{selected_thread}/details"
    ).json()

    st.session_state["thread_id"] = selected_thread
    thread_key=st.session_state["thread_id"]

    st.session_state["message_history"] = (
        details["messages"]
    )

    # --------------------
    # Load YouTube
    # --------------------
    try:
        yt = requests.get(
            API_GET_YT.format(thread_id=selected_thread)
        )

        if yt.status_code == 200:
            data = yt.json()

            if data["youtube_url"]:
                st.session_state["youtube_url"] = (
                    data["youtube_url"][0]
                )
            else:
                st.session_state["youtube_url"] = None
    except:
        st.session_state["youtube_url"] = None

    # --------------------
    # Load PDF state
    # --------------------
    docs = requests.get(
        API_THREAD_DOCS.format(
            thread_id=selected_thread
        )
    ).json()

    st.session_state["pdf_uploaded"] = any(
        doc["type"] == "pdf"
        for doc in docs["documents"]
    )

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