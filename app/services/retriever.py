STOP_PHRASES = [
    "教えてください",
    "どのように",
    "について",
    "教えて",
    "ください",
    "ですか",
    "ますか",
    "します",
    "です",
    "ます",
    "とは",
    "どう",
    "する",
]

PARTICLES = ["は", "が", "を", "に", "の", "へ", "と", "も", "で", "や", "か"]
MARKS = ["、", "。", "？", "?", "！", "!", ".", ",", "（", "）", "(", ")"]


def _extract_keywords(question: str) -> list[str]:
    cleaned = question
    for word in STOP_PHRASES:
        cleaned = cleaned.replace(word, " ")

    for mark in MARKS:
        cleaned = cleaned.replace(mark, " ")

    keywords = []
    for phrase in cleaned.split():
        keyword = phrase.strip("".join(PARTICLES))
        if len(keyword) >= 2:
            keywords.append(keyword)

    for particle in PARTICLES:
        cleaned = cleaned.replace(particle, " ")

    for word in STOP_PHRASES:
        cleaned = cleaned.replace(word, " ")

    for word in cleaned.split():
        keyword = word.strip("".join(PARTICLES))
        if len(keyword) >= 2:
            keywords.append(keyword)

    return list(dict.fromkeys(keywords))


def _score_chunk(question: str, keywords: list[str], chunk: dict) -> int:
    text = chunk["text"]
    score = 0

    compact_question = question.strip()
    if len(compact_question) >= 4 and compact_question in text:
        score += 5

    for keyword in keywords:
        if keyword not in text:
            continue

        score += 1
        if len(keyword) >= 4:
            score += 1
        if "の" in keyword:
            score += 2

    return score


def search_relevant_chunks(question: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    normalized_question = question.strip()
    if len(normalized_question) < 2 or top_k < 1:
        return []

    keywords = _extract_keywords(normalized_question)
    if not keywords:
        return []

    scored_chunks = []
    for index, chunk in enumerate(chunks):
        score = _score_chunk(normalized_question, keywords, chunk)
        if score > 0:
            scored_chunks.append((score, index, chunk))

    scored_chunks.sort(key=lambda item: (-item[0], item[1]))

    return [chunk for _score, _index, chunk in scored_chunks[:top_k]]
