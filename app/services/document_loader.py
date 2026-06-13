from pathlib import Path

from app.services.pdf_loader import load_pdf_chunks


FAQ_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_faq.txt"
PDF_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_policy.pdf"


def load_faq_text() -> str:
    if not FAQ_PATH.exists():
        raise FileNotFoundError

    text = FAQ_PATH.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError

    return text


def load_document_chunks() -> list[dict]:
    return load_pdf_chunks(PDF_PATH)
