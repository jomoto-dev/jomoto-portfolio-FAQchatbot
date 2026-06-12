def split_into_chunks(text: str) -> list[str]:
    # FAQ本文を空行ごとに分割します。
    return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
