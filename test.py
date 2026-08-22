import sqlite3
import os
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "chatbot_conv.db")

os.makedirs(DB_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor=conn.cursor()
data=cursor.execute("""
CREATE TABLE  documents (
    doc_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type TEXT,
    content_hash TEXT NOT NULL,
    source TEXT,
    vectorstore_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
);
""")

for d in data:
    print(d)

conn.commit()

conn.close()