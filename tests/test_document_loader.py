import pytest

from app.services import document_loader
from app.services.document_loader import load_faq_text


def test_load_faq_text_returns_text(monkeypatch, tmp_path):
    faq_path = tmp_path / "sample_faq.txt"
    faq_path.write_text("Q. テスト\nA. 回答", encoding="utf-8")
    monkeypatch.setattr(document_loader, "FAQ_PATH", faq_path)

    assert load_faq_text() == "Q. テスト\nA. 回答"


def test_load_faq_text_raises_when_file_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(document_loader, "FAQ_PATH", tmp_path / "missing.txt")

    with pytest.raises(FileNotFoundError):
        load_faq_text()


def test_load_faq_text_raises_when_file_is_empty(monkeypatch, tmp_path):
    faq_path = tmp_path / "sample_faq.txt"
    faq_path.write_text("   \n\t", encoding="utf-8")
    monkeypatch.setattr(document_loader, "FAQ_PATH", faq_path)

    with pytest.raises(ValueError):
        load_faq_text()
