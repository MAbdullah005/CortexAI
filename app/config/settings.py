
"""
Project Settings

Central configuration file for the entire AI Agent system.
All constants and environment-based configurations live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# =================================
# Application
# =================================

APP_NAME = "OmniAgent AI"
APP_VERSION = "1.0.0"


# =================================
# LLM Settings
# =================================

USE_OPENAI = False

OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_TEMPERATURE = 0.2

OPENAI_MODEL = "gpt-4o-mini"


# =================================
# Embedding Settings
# =================================

EMBEDDING_MODEL = "nomic-embed-text"


# =================================
# RAG Settings
# =================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

RETRIEVAL_K = 4


# =================================
# File Paths
# =================================

DATA_DIR = "data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
VECTORSTORE_DIR = os.path.join(DATA_DIR, "vectorstore")

DATABASE_DIR = "database"
SQLITE_DB_PATH = os.path.join(DATABASE_DIR, "chatbot_conv.db")


# =================================
# API Keys
# =================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


# =================================
# Logging
# =================================

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")


# =================================
# Tool Settings
# =================================

WEB_SEARCH_REGION = "us-en"


# =================================
# Security / Limits
# =================================

MAX_PDF_SIZE_MB = 25
MAX_CHAT_HISTORY = 20