import streamlit as st

from api_client import (
    login,
    signup,
    forgot_password,
)


# ============================================================
# AUTH STATE
# ============================================================

def initialize_auth_state():
    """
    Initialize authentication-related Streamlit state.
    """

    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"


# ============================================================
# LOGIN
# ============================================================

def login_page():

    st.title("🔐 Login")

    st.write("Login to continue to your AI chatbot.")

    st.divider()

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button(
        "Login",
        use_container_width=True,
        type="primary"
    ):

        if not email or not password:
            st.error("Email and password are required.")
            return

        response = login(
            email=email.strip().lower(),
            password=password
        )

        if response is None:
            st.error(
                "Unable to connect to the backend."
            )
            return

        if response.status_code == 200:

            data = response.json()

            st.session_state["access_token"] = (
                data["access_token"]
            )

            # Get current user
            from api_client import get_current_user

            me_response = get_current_user(
                data["access_token"]
            )

            if (
                me_response is not None
                and me_response.status_code == 200
            ):
                st.session_state["user"] = (
                    me_response.json()
                )

            else:
                # Login succeeded but user information
                # could not be loaded.
                st.session_state["access_token"] = None
                st.error(
                    "Login succeeded, but user information "
                    "could not be loaded."
                )
                return

            st.success("Login successful!")

            st.rerun()

        else:

            try:
                detail = response.json().get(
                    "detail",
                    "Login failed."
                )
            except Exception:
                detail = "Login failed."

            st.error(detail)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Create account",
            use_container_width=True
        ):
            st.session_state["auth_page"] = "signup"
            st.rerun()

    with col2:
        if st.button(
            "Forgot password?",
            use_container_width=True
        ):
            st.session_state["auth_page"] = "forgot"
            st.rerun()


# ============================================================
# SIGNUP
# ============================================================

def signup_page():

    st.title("📝 Create Account")

    st.write(
        "Create an account to use the AI chatbot."
    )

    st.divider()

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key="signup_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="At least 8 characters",
        key="signup_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Repeat your password",
        key="signup_confirm_password"
    )

    if st.button(
        "Create Account",
        use_container_width=True,
        type="primary"
    ):

        if not email or not password:
            st.error(
                "Email and password are required."
            )
            return

        if password != confirm_password:
            st.error(
                "Passwords do not match."
            )
            return

        if len(password) < 8:
            st.error(
                "Password must be at least 8 characters."
            )
            return

        if len(password.encode("utf-8")) > 70:
            st.error(
                "Password is too long."
            )
            return

        response = signup(
            email=email.strip().lower(),
            password=password
        )

        if response is None:
            st.error(
                "Unable to connect to the backend."
            )
            return

        if response.status_code == 200:

            st.success(
                "Account created successfully!"
            )

            st.info(
                "📧 Please check your email and "
                "click the verification link before logging in."
            )

            st.session_state["auth_page"] = "login"

            st.rerun()

        else:

            try:
                detail = response.json().get(
                    "detail",
                    "Signup failed."
                )
            except Exception:
                detail = "Signup failed."

            st.error(detail)

    st.divider()

    if st.button(
        "Already have an account? Login",
        use_container_width=True
    ):
        st.session_state["auth_page"] = "login"
        st.rerun()


# ============================================================
# FORGOT PASSWORD
# ============================================================

def forgot_password_page():

    st.title("🔑 Forgot Password")

    st.write(
        "Enter your email and we'll send you "
        "a password reset link."
    )

    st.divider()

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key="forgot_email"
    )

    if st.button(
        "Send Reset Link",
        use_container_width=True,
        type="primary"
    ):

        if not email:
            st.error("Email is required.")
            return

        response = forgot_password(
            email.strip().lower()
        )

        if response is None:
            st.error(
                "Unable to connect to the backend."
            )
            return

        if response.status_code == 200:

            st.success(
                "If this email exists, "
                "a password reset link has been sent."
            )

        else:

            try:
                detail = response.json().get(
                    "detail",
                    "Unable to send reset link."
                )
            except Exception:
                detail = "Unable to send reset link."

            st.error(detail)

    st.divider()

    if st.button(
        "Back to Login",
        use_container_width=True
    ):
        st.session_state["auth_page"] = "login"
        st.rerun()


# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.session_state["access_token"] = None
    st.session_state["user"] = None

    # Clear chat-related state too
    keys_to_remove = [
        "thread_id",
        "message_history",
        "youtube_url",
        "pdf_uploaded",
        "youtube_loaded_for",
        "sources",
        "uploaded_file_name",
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)

    st.session_state["auth_page"] = "login"

    st.rerun()


# ============================================================
# AUTHENTICATION CHECK
# ============================================================

def is_authenticated():

    return bool(
        st.session_state.get("access_token")
        and st.session_state.get("user")
    )


# ============================================================
# AUTH UI ENTRY POINT
# ============================================================

def render_auth():

    initialize_auth_state()

    if is_authenticated():
        return True

    if st.session_state["auth_page"] == "login":

        login_page()

    elif st.session_state["auth_page"] == "signup":

        signup_page()

    elif st.session_state["auth_page"] == "forgot":

        forgot_password_page()

    return False