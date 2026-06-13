import re
from pathlib import Path


def _normalize_chunk_text(text: str) -> str:
    return " ".join(text.split())


def split_pdf_text_into_chunks(text: str) -> list[str]:
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = "\n".join(cleaned_lines)
    if not cleaned_text:
        return []

    article_matches = list(re.finditer(r"第[0-9０-９]+条", cleaned_text))
    if article_matches:
        chunks = []
        for index, match in enumerate(article_matches):
            start = match.start()
            if index + 1 < len(article_matches):
                end = article_matches[index + 1].start()
            else:
                end = len(cleaned_text)

            chunk_text = _normalize_chunk_text(cleaned_text[start:end])
            if chunk_text:
                chunks.append(chunk_text)

        return chunks

    paragraphs = re.split(r"\n\s*\n", text.strip())
    chunks = [_normalize_chunk_text(paragraph) for paragraph in paragraphs if paragraph.strip()]
    if len(chunks) > 1:
        return chunks

    return [_normalize_chunk_text(line) for line in cleaned_lines]


def load_pdf_chunks(pdf_path: Path, source_name: str | None = None) -> list[dict]:
    if not pdf_path.exists():
        raise FileNotFoundError

    import fitz

    chunks = []
    chunk_number = 1
    source = source_name or pdf_path.name

    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            page_chunks = split_pdf_text_into_chunks(page.get_text())

            for text in page_chunks:
                chunks.append(
                    {
                        "text": text,
                        "source": source,
                        "page": page_index,
                        "chunk_id": f"chunk_{chunk_number:03d}",
                    }
                )
                chunk_number += 1

    if not chunks:
        raise ValueError

    return chunks
