def detect_source(query: str):

    q = query.lower()

    pdf_words = [
        "pdf",
        "document",
        "resume",
        "file"
    ]

    yt_words = [
        "youtube",
        "video",
        "transcript",
        "lecture"
    ]

    pdf_hit = any(word in q for word in pdf_words)
    yt_hit = any(word in q for word in yt_words)

    if pdf_hit and yt_hit:
        return None

    if pdf_hit:
        return "pdf"

    if yt_hit:
        return "youtube"

    return None