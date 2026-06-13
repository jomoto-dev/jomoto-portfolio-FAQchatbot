from pathlib import Path


FAQ_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_faq.txt"


def load_faq_text() -> str:
    if not FAQ_PATH.exists():
        raise FileNotFoundError

    text = FAQ_PATH.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError

    return text
