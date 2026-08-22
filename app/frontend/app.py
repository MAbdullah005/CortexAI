import streamlit as st

from auth_ui import render_auth
from chat_ui import render_chat_ui


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Multi-Utility Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# AUTHENTICATION
# ============================================================

if not render_auth():
    st.stop()


# ============================================================
# AUTHENTICATED APPLICATION
# ============================================================

render_chat_ui()