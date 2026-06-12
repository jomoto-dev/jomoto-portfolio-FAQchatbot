from pathlib import Path


FAQ_FILE = Path(__file__).resolve().parents[2] / "data" / "sample_faq.txt"


def load_faq_text() -> str:
    # FAQファイルの本文を読み込みます。
    return FAQ_FILE.read_text(encoding="utf-8")
