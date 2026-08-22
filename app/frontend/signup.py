import streamlit as st
import requests
from app.frontend.streamlit_app import API_SIGNUP
def signup_page():

    st.title("📝 Create Account")

    email = st.text_input(
        "Email",
        key="signup_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="signup_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="signup_confirm_password"
    )

    if st.button(
        "Create Account",
        use_container_width=True
    ):

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        response = requests.post(
            API_SIGNUP,
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code == 200:

            st.success(
                "Account created! "
                "Please check your email and verify your account."
            )

            st.session_state["auth_page"] = "login"

            st.rerun()

        else:

            try:
                st.error(response.json()["detail"])
            except Exception:
                st.error("Signup failed.")