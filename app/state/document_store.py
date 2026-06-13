current_chunks: list[dict] = []
current_source: str | None = None


def set_current_document(chunks: list[dict], source: str) -> None:
    global current_chunks, current_source
    current_chunks = chunks
    current_source = source


def get_current_chunks() -> list[dict]:
    return current_chunks


def get_current_source() -> str | None:
    return current_source


def clear_current_document() -> None:
    global current_chunks, current_source
    current_chunks = []
    current_source = None
