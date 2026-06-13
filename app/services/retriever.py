def _extract_keywords(question: str) -> list[str]:
    cleaned = question
    for word in ["について", "教えてください", "教えて", "ください", "ですか", "ますか", "とは"]:
        cleaned = cleaned.replace(word, " ")

    for mark in ["、", "。", "？", "?", "！", "!", "。", ".", ","]:
        cleaned = cleaned.replace(mark, " ")

    keywords = []
    for word in cleaned.split():
        keyword = word.strip(" はをがのにでとも")
        if len(keyword) >= 2:
            keywords.append(keyword)

    return keywords


def search_best_chunk(question: str, chunks: list[dict]) -> dict | None:
    normalized_question = question.strip()
    if len(normalized_question) < 2:
        return None

    keywords = _extract_keywords(normalized_question)
    if not keywords:
        return None

    best_chunk = None
    best_score = 0

    for chunk in chunks:
        text = chunk["text"]
        score = sum(1 for keyword in keywords if keyword and keyword in text)
        if score > best_score:
            best_chunk = chunk
            best_score = score

    if best_score == 0:
        return None

    return best_chunk
