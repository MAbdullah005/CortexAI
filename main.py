from fastapi import FastAPI
#from app.rag import chat, rag, threads
from app.services import chat_service,pdf_service
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from fastapi import APIRouter, UploadFile, File


# Register routes
#app.include_router(chat.router, prefix="/chat", tags=["Chat"])
#app.include_router(rag.router, prefix="/rag", tags=["RAG"])
#app.include_router(threads.router, prefix="/threads", tags=["Threads"])
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAG Chatbot API")
#s
app.include_router(router)
"""


@app.get("/")
def root():
    return {"message": "API is running"}


from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from app.graph.agent_graph import chatbot

router = APIRouter()


@router.post("/")
def chat_endpoint(request: dict):
    user_input = request.get("message")
    thread_id = request.get("thread_id")

    config = {
        "configurable": {"thread_id": thread_id},
        "run_name": "api_chat",
    }

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )

    return {
        "response": response["messages"][-1].content,
        "thread_id": thread_id,
    }




@router.post("/stream")
def chat_stream(request: dict):

    user_input = request.get("message")
    thread_id = request.get("thread_id")

    config = {
        "configurable": {"thread_id": thread_id},
    }

    def event_generator():
        for event in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages",
        ):
            message = event[0]
            if hasattr(message, "content"):
                yield message.content

    return StreamingResponse(event_generator(), media_type="text/plain")




router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), thread_id: str = ""):

    content = await file.read()

    summary = ingest_pdf(
        content,
        thread_id=thread_id,
        filename=file.filename,
    )

    return {
        "status": "success",
        "data": summary
    }
    """