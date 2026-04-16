
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from app.services.youtube_loader import load_youtube_transcript

embeddings = OllamaEmbeddings(model="nomic-embed-text")

def build_youtube_retriever(url: str):
    text = load_youtube_transcript(url)

    if not text:
        raise ValueError("No transcript available")

    # 🔹 Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    docs = splitter.create_documents([text])

    # 🔹 Vector store
    vectorstore = FAISS.from_documents(docs, embeddings)

    return vectorstore.as_retriever(search_kwargs={"k": 3})