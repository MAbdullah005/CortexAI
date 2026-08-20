from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from jose import JWTError

from app.auth.jwt_utils import decode_access_token
import sqlite3


DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chatbot_conv.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)


# ================================
# OAuth2 / JWT Configuration
# ================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ================================
# Get Current Authenticated User
# ================================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """
    Validate the JWT access token and return
    the authenticated user from the database.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        # Decode and validate JWT
        payload = decode_access_token(token)

        # Extract user ID from JWT
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    # ================================
    # Find User in SQLite
    # ================================

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

    if row is None:
        raise credentials_exception

    # Return user as dictionary
    return {
        "user_id": row[0],
        "email": row[1],
        "password_hash": row[2],
        "is_verified": bool(row[3]),
        "created_at": row[4],
    }