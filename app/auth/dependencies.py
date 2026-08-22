import os
import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.auth.jwt_utils import decode_access_token


DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chatbot_conv.db")


conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)


# =================================
# HTTP Bearer Authentication
# =================================

security = HTTPBearer()


# =================================
# Get Current Authenticated User
# =================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate JWT access token and return
    the authenticated user from SQLite.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # =================================
    # Extract JWT token
    # =================================

    token = credentials.credentials

    # =================================
    # Decode JWT
    # =================================

    try:

        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError, TypeError):

        raise credentials_exception

    # =================================
    # Find User
    # =================================

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                user_id,
                email,
                password_hash,
                is_verified,
                created_at
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = cursor.fetchone()

    except Exception:

        raise credentials_exception

    # =================================
    # User doesn't exist
    # =================================

    if row is None:
        raise credentials_exception

    # =================================
    # Return authenticated user
    # =================================

    return {
        "user_id": row[0],
        "email": row[1],
        "password_hash": row[2],
        "is_verified": bool(row[3]),
        "created_at": row[4],
    }