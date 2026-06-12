def _extract_keywords(question: str) -> list[str]:
    cleaned = question
    for word in ["について", "教えてください", "教えて", "ください", "ですか", "ますか", "とは"]:
        cleaned = cleaned.replace(word, " ")

    for mark in ["、", "。", "？", "?", "！", "!", "。", ".", ","]:
        cleaned = cleaned.replace(mark, " ")

    return [word.strip(" はをがのにでとも") for word in cleaned.split() if word.strip()]


def search_best_chunk(question: str, chunks: list[str]) -> tuple[str | None, int]:
    keywords = _extract_keywords(question)
    best_index = -1
    best_score = 0

    for index, chunk in enumerate(chunks):
        score = sum(1 for keyword in keywords if keyword and keyword in chunk)
        if score > best_score:
            best_index = index
            best_score = score

    if best_score == 0:
        return None, -1

    return chunks[best_index], best_index
