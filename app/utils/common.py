def extract_ai_text(message):
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))

            else:
                text = getattr(block, "text", None)
                if text:
                    text_parts.append(text)

        return "\n".join(text_parts)

    return str(content)


def is_valid_chunk(text: str) -> bool:
    """
    Filter useless chunks before embedding
    """

    if len(text.strip()) < 50:
        return False

    if text.count(" ") < 5:
        return False

    return True