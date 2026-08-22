import requests
from app.frontend.streamlit_app import API_LOGIN,API_ME
from app.utils.common import auth_headers
import streamlit as st

def login_page():

    st.title("🔐 Login")

    email = st.text_input(
        "Email",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login", use_container_width=True):

        response = requests.post(
            API_LOGIN,
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state["access_token"] = (
                data["access_token"]
            )

            me_response = requests.get(
                API_ME,
                headers=auth_headers()
            )

            if me_response.status_code == 200:
                st.session_state["user"] = (
                    me_response.json()
                )

            st.rerun()

        else:
            try:
                st.error(response.json()["detail"])
            except Exception:
                st.error("Login failed.")


