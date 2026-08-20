from fastapi import FastAPI

from app.api.routes import router as api_router
from app.auth.routes import router as auth_router


app = FastAPI(
    title="RAG Chatbot API"
)


# Main chatbot APIs
app.include_router(api_router)

# Authentication APIs
app.include_router(auth_router)