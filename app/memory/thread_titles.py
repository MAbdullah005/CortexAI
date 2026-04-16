import streamlit as st

def set_thread_title(thread_id: str, title: str):
    if "thread_titles" not in st.session_state:
        st.session_state["thread_titles"] = {}

    st.session_state["thread_titles"][str(thread_id)] = title


def get_thread_title(thread_id: str) -> str:
    if "thread_titles" not in st.session_state:
        st.session_state["thread_titles"] = {}

    return st.session_state["thread_titles"].get(
        str(thread_id), f"Chat {str(thread_id)[:6]}"
    )
