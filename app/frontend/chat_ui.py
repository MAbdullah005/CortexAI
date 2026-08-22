import json
import uuid

import streamlit as st

from api_client import (
    create_thread,
    get_threads,
    get_thread_details,
    get_thread_documents,
    get_thread_sources,
    send_message,
    set_youtube,
    get_youtube,
    upload_pdf,
    generate_title,
    get_pdf,
)
from auth_ui import logout
import base64

# ============================================================
# INITIALIZE CHAT STATE
# ============================================================

def initialize_chat_state():

    if "message_history" not in st.session_state:
        st.session_state["message_history"] = []

    if "youtube_url" not in st.session_state:
        st.session_state["youtube_url"] = None

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = None

    if "pdf_uploaded" not in st.session_state:
        st.session_state["pdf_uploaded"] = False

    if "youtube_loaded_for" not in st.session_state:
        st.session_state["youtube_loaded_for"] = None

    if "sources" not in st.session_state:
        st.session_state["sources"] = {}

    if "uploaded_file_name" not in st.session_state:
        st.session_state["uploaded_file_name"] = None

    if "selected_thread" not in st.session_state:
        st.session_state["selected_thread"] = None


# ============================================================
# CREATE INITIAL THREAD
# ============================================================

def ensure_thread():

    if st.session_state.get("thread_id"):
        return

    token = st.session_state["access_token"]

    response = create_thread(token)

    if response is None:
        st.error("Unable to connect to backend.")
        st.stop()

    if response.status_code != 200:
        st.error(
            f"Failed to create thread: "
            f"{response.text}"
        )
        st.stop()

    data = response.json()

    st.session_state["thread_id"] = data["thread_id"]


# ============================================================
# RESET THREAD STATE
# ============================================================

def reset_thread_state():

    st.session_state["message_history"] = []
    st.session_state["youtube_url"] = None
    st.session_state["pdf_uploaded"] = False
    st.session_state["youtube_loaded_for"] = None
    st.session_state["sources"] = {}
    st.session_state["uploaded_file_name"] = None


# ============================================================
# CREATE NEW CHAT
# ============================================================

def create_new_chat():

    token = st.session_state["access_token"]

    response = create_thread(token)

    if response is None:
        st.sidebar.error(
            "Unable to connect to backend."
        )
        return

    if response.status_code != 200:
        st.sidebar.error(
            "Failed to create new chat."
        )
        return

    data = response.json()

    st.session_state["thread_id"] = data["thread_id"]

    reset_thread_state()

    st.rerun()


# ============================================================
# LOAD THREAD
# ============================================================

def load_thread(thread_id):

    token = st.session_state["access_token"]

    response = get_thread_details(
        token,
        thread_id
    )

    if response is None:
        st.error(
            "Unable to connect to backend."
        )
        return

    if response.status_code != 200:

        # Token may have expired.
        if response.status_code == 401:
            logout()
            return

        st.error(
            f"Failed to load thread: "
            f"{response.text}"
        )
        return

    details = response.json()

    st.session_state["thread_id"] = thread_id

    st.session_state["message_history"] = (
        details.get("messages", [])
    )

    # ---------------------------------------------
    # Load YouTube
    # ---------------------------------------------

    try:

        yt_response = get_youtube(
            token,
            thread_id
        )

        if (
            yt_response is not None
            and yt_response.status_code == 200
        ):

            yt_data = yt_response.json()

            urls = yt_data.get(
                "youtube_url"
            )

            if urls:
                st.session_state["youtube_url"] = urls[0]
            else:
                st.session_state["youtube_url"] = None

    except Exception:

        st.session_state["youtube_url"] = None

    # ---------------------------------------------
    # Load PDF state
    # ---------------------------------------------

    try:

        docs_response = get_thread_documents(
            token,
            thread_id
        )

        if (
            docs_response is not None
            and docs_response.status_code == 200
        ):

            docs_data = docs_response.json()

            documents = docs_data.get(
                "documents",
                []
            )

            st.session_state["pdf_uploaded"] = any(
                doc.get("type") == "pdf"
                for doc in documents
            )

    except Exception:

        st.session_state["pdf_uploaded"] = False

    st.session_state["selected_thread"] = None

    st.rerun()


# ============================================================
# CHAT MESSAGE API
# ============================================================

def call_chat_api(user_input, thread_id):

    token = st.session_state["access_token"]

    response = send_message(
        token,
        user_input,
        thread_id
    )

    if response is None:
        return "❌ Unable to connect to backend."

    if response.status_code == 401:
        logout()
        return "❌ Session expired. Please login again."

    if response.status_code != 200:

        try:
            detail = response.json().get(
                "detail",
                "Unknown API error"
            )
        except Exception:
            detail = response.text

        return f"❌ API Error: {detail}"

    try:

        return response.json().get(
            "response",
            "⚠️ No response"
        )

    except Exception:

        return "⚠️ Invalid response from server."


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    token = st.session_state["access_token"]
    user = st.session_state["user"]

    st.sidebar.title(
        "LangGraph Multi-Tool Chatbot"
    )

    # ---------------------------------------------
    # User
    # ---------------------------------------------

    st.sidebar.write(
        f"👤 {user.get('email', 'User')}"
    )

    st.sidebar.divider()

    # ---------------------------------------------
    # Current Thread
    # ---------------------------------------------

    thread_id = st.session_state["thread_id"]

    if thread_id:

        st.sidebar.markdown(
            f"**Thread ID:** `{thread_id[:8]}`"
        )

    # ---------------------------------------------
    # New Chat
    # ---------------------------------------------

    if st.sidebar.button(
        "➕ New Chat",
        use_container_width=True
    ):

        create_new_chat()

    # ---------------------------------------------
    # Clear Conversation
    # ---------------------------------------------

    if st.sidebar.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state[
            "message_history"
        ] = []

        st.rerun()

    st.sidebar.divider()

    # ========================================================
    # PDF
    # ========================================================

    uploaded_pdf = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_pdf:

        if (
            uploaded_pdf.name
            != st.session_state["uploaded_file_name"]
        ):

            response = upload_pdf(
                token,
                thread_id,
                uploaded_pdf
            )

            if response is None:

                st.sidebar.error(
                    "Unable to connect to backend."
                )

            elif response.status_code == 200:

                st.session_state[
                    "pdf_uploaded"
                ] = True

                st.session_state[
                    "uploaded_file_name"
                ] = uploaded_pdf.name

                st.sidebar.success(
                    "✅ PDF uploaded successfully"
                )

            elif response.status_code == 401:

                logout()

            else:

                try:
                    detail = response.json().get(
                        "detail",
                        "PDF upload failed."
                    )
                except Exception:
                    detail = "PDF upload failed."

                st.sidebar.error(detail)

    st.sidebar.divider()

    # ========================================================
    # YOUTUBE
    # ========================================================

    st.sidebar.subheader(
        "🎥 YouTube Video"
    )

    youtube_url = st.sidebar.text_input(
        "Paste YouTube URL",
        key="youtube_input"
    )

    if st.sidebar.button(
        "Load Video",
        use_container_width=True
    ):

        if not youtube_url:

            st.sidebar.warning(
                "Please enter a YouTube URL."
            )

        else:

            response = set_youtube(
                token,
                thread_id,
                youtube_url
            )

            if response is None:

                st.sidebar.error(
                    "Unable to connect to backend."
                )

            elif response.status_code == 200:

                st.session_state[
                    "youtube_url"
                ] = youtube_url

                st.session_state[
                    "youtube_loaded_for"
                ] = thread_id

                st.sidebar.success(
                    "✅ Video loaded successfully"
                )

            elif response.status_code == 401:

                logout()

            else:

                try:
                    detail = response.json().get(
                        "detail",
                        "Failed to load video."
                    )
                except Exception:
                    detail = "Failed to load video."

                st.sidebar.error(detail)

    # ========================================================
    # PAST CONVERSATIONS
    # ========================================================

    st.sidebar.divider()

    st.sidebar.subheader(
        "💬 Past Conversations"
    )

    response = get_threads(token)

    if response is not None:

        if response.status_code == 200:

            threads = response.json()

            for thread in threads:

                title = (
                    thread.get("title")
                    or f"Chat {thread['thread_id'][:6]}"
                )

                if st.sidebar.button(
                    title,
                    key=f"thread_{thread['thread_id']}",
                    use_container_width=True
                ):

                    load_thread(
                        thread["thread_id"]
                    )

        elif response.status_code == 401:

            logout()

        else:

            st.sidebar.error(
                "Failed to load conversations."
            )

    # ========================================================
    # LOGOUT
    # ========================================================

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()


# ============================================================
# CHAT AREA
# ============================================================

def render_chat():

    thread_id = st.session_state["thread_id"]

    st.subheader("💬 Chat")

    chat_container = st.container()

    with chat_container:

        for message in st.session_state[
            "message_history"
        ]:

            with st.chat_message(
                message["role"]
            ):

                st.write(
                    message["content"]
                )

    user_input = st.chat_input(
        "Ask something..."
    )

    if user_input:

        st.session_state[
            "message_history"
        ].append(
            {
                "role": "user",
                "content": user_input
            }
        )

        st.session_state[
            "message_history"
        ].append(
            {
                "role": "assistant",
                "content": "⏳ Thinking..."
            }
        )

        st.rerun()

    # ---------------------------------------------
    # Process pending message
    # ---------------------------------------------

    if st.session_state["message_history"]:

        last_message = (
            st.session_state[
                "message_history"
            ][-1]
        )

        if (
            last_message["role"] == "assistant"
            and
            last_message["content"] == "⏳ Thinking..."
        ):

            user_message = (
                st.session_state[
                    "message_history"
                ][-2]["content"]
            )

            ai_message = call_chat_api(
                user_message,
                thread_id
            )

            st.session_state[
                "message_history"
            ][-1]["content"] = ai_message

            # -------------------------------------
            # Generate title after first message
            # -------------------------------------

            if len(
                st.session_state[
                    "message_history"
                ]
            ) == 2:

                user = st.session_state["user"]

                try:

                    generate_title(
                        st.session_state[
                            "access_token"
                        ],
                        thread_id,
                        user["user_id"],
                        user_message
                    )

                except Exception:
                    pass

            st.rerun()


# ============================================================
# VIDEO + PDF
# ============================================================

def render_media():

    thread_id = st.session_state["thread_id"]

    st.subheader(
        "🎥 Video + 📄 Document"
    )

    # ========================================================
    # VIDEO
    # ========================================================

    if st.session_state.get(
        "youtube_url"
    ):

        st.video(
            st.session_state[
                "youtube_url"
            ]
        )

    else:

        st.info(
            "No video loaded"
        )

    st.markdown(
        "<div style='margin-top:10px'></div>",
        unsafe_allow_html=True
    )

    # ========================================================
    # PDF
    # ========================================================

    if st.session_state.get("pdf_uploaded"):

      pdf_response = get_pdf(thread_id)

      if pdf_response is not None and pdf_response.status_code == 200:

        pdf_base64 = base64.b64encode(
            pdf_response.content
        ).decode("utf-8")

        pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{pdf_base64}"
            width="100%"
            height="600px"
            style="border:none;">
        </iframe>
        """

        st.markdown(
            pdf_html,
            unsafe_allow_html=True
        )

      else:

        if pdf_response is None:
            st.error("Failed to connect to PDF API")

        else:
            try:
                detail = pdf_response.json().get(
                    "detail",
                    "Unknown error"
                )
            except Exception:
                detail = pdf_response.text

            st.error(
                f"PDF Error ({pdf_response.status_code}): {detail}"
            )

    else:

      st.info("Upload a PDF to view it here")

# ============================================================
# DOWNLOAD CHAT
# ============================================================

def render_download():

    st.divider()

    chat_json = json.dumps(
        st.session_state[
            "message_history"
        ],
        indent=2
    )

    st.download_button(
        label="⬇️ Download Chat History",
        data=chat_json,
        file_name="chat_history.json",
        mime="application/json"
    )


# ============================================================
# MAIN CHAT UI
# ============================================================

def render_chat_ui():

    initialize_chat_state()

    ensure_thread()

    # --------------------------------------------------------
    # Global UI
    # --------------------------------------------------------

    st.markdown(
        """
        <style>
        .block-container {
            padding: 0rem !important;
        }

        .main > div {
            gap: 0rem !important;
        }

        section[data-testid="stSidebar"] {
            width: 240px !important;
        }

        div[data-testid="column"] {
            padding: 0px !important;
        }

        .chat-box {
            height: 80vh;
            overflow-y: auto;
        }

        .video-box {
            height: 90vh;
            overflow-y: auto;
            padding: 0px;
            margin: 0px;
        }

        .element-container {
            margin-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

    render_sidebar()

    # --------------------------------------------------------
    # Main title
    # --------------------------------------------------------

    st.title(
        "Multi Utility Chatbot"
    )

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    split_ratio = st.slider(
        "Resize Chat ↔ Video",
        10,
        90,
        70
    )

    col_video, col_chat = st.columns(
        [
            100 - split_ratio,
            split_ratio
        ],
        gap="small"
    )

    # --------------------------------------------------------
    # Chat
    # --------------------------------------------------------

    with col_chat:

        render_chat()

    # --------------------------------------------------------
    # Video + PDF
    # --------------------------------------------------------

    with col_video:

        render_media()

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    render_download()