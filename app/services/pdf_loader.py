import re
from pathlib import Path


def _is_page_number_line(line: str) -> bool:
    if re.fullmatch(r"\d+", line):
        return True

    return re.fullmatch(r"[-ー－―]\s*\d+\s*[-ー－―]", line) is not None


def clean_extracted_text(text: str) -> str:
    cleaned_lines = []
    previous_line_was_blank = False

    for raw_line in text.strip().splitlines():
        line = re.sub(r"[ \t\u3000]+", " ", raw_line.strip())

        if not line:
            if cleaned_lines and not previous_line_was_blank:
                cleaned_lines.append("")
            previous_line_was_blank = True
            continue

        if _is_page_number_line(line):
            continue

        cleaned_lines.append(line)
        previous_line_was_blank = False

    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


def _normalize_chunk_text(text: str) -> str:
    cleaned_text = clean_extracted_text(text)
    lines = [line.strip() for line in cleaned_text.splitlines()]

    return "\n".join(line for line in lines if line)


def split_pdf_text_into_chunks(text: str) -> list[str]:
    text = clean_extracted_text(text)
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
            page_text = clean_extracted_text(page.get_text())
            page_chunks = split_pdf_text_into_chunks(page_text)

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
