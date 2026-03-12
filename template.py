import os

folders = [
    "app/frontend",
    "app/graph",
    "app/rag",
    "app/tools",
    "app/llm",
    "app/memory",
    "app/services",
    "app/utils",
    "app/config",
    "data/vectorstore",
    "data/uploads",
    "database",
    "tests",
    "scripts"
]

files = [
    "app/frontend/streamlit_app.py",
    "app/graph/agent_graph.py",
    "app/graph/nodes.py",
    "app/graph/state.py",
    "app/rag/ingest.py",
    "app/rag/retriever.py",
    "app/rag/vector_store.py",
    "app/tools/calculator_tool.py",
    "app/tools/stock_tool.py",
    "app/tools/search_tool.py",
    "app/tools/rag_tool.py",
    "app/tools/python_executor.py",
    "app/llm/llm_config.py",
    "app/memory/sqlite_memory.py",
    "app/services/chat_service.py",
    "app/services/pdf_service.py",
    "app/utils/thread_utils.py",
    "app/utils/logger.py",
    "app/config/settings.py",
    "tests/test_tools.py",
    "tests/test_rag.py",
    "tests/test_agent.py",
    "scripts/create_project_structure.py",
    "requirements.txt",
    ".env",
    ".gitignore",
    "README.md",
    "run_streamlit.py"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in files:
    if not os.path.exists(file):
        with open(file, "w") as f:
            pass

print("✅ Project structure created successfully!")