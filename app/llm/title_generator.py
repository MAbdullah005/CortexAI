from app.llm.llm_config import gen_title

TITLE_PROMPT = """
You are generating a short chat title.

Rules:
- Max 5 words
- No punctuation
- No quotes
- No emojis
- Just the title
- Use Title Case

User message:
{message}

Title:
"""

def generate_chat_title(message: str) -> str:
    prompt = TITLE_PROMPT.format(message=message)
    response = gen_title.invoke(prompt)
    title = response.content.strip()
    title = title.replace("Title:", "").strip()
    return title