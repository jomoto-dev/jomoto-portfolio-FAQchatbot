current_chunks: list[dict] = []


def set_current_document(chunks: list[dict]) -> None:
    global current_chunks
    current_chunks = chunks


def get_current_chunks() -> list[dict]:
    return current_chunks


def clear_current_document() -> None:
    global current_chunks
    current_chunks = []
