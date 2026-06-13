from fastapi.testclient import TestClient

from app.main import app


# FastAPIアプリをテスト用クライアントで呼び出します。
client = TestClient(app)


def test_index_returns_ok():
    response = client.get("/")

    assert response.status_code == 200


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_returns_answer_and_citations():
    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )
    data = response.json()

    assert response.status_code == 200
    assert "answer" in data
    assert "citations" in data
    assert data["citations"]
    assert "返金" in data["answer"]
    assert "営業時間" not in data["answer"]
    assert "領収書" not in data["answer"]

    citation = data["citations"][0]
    assert set(citation) == {"source", "page", "chunk_id", "text"}


def test_ask_returns_400_when_question_is_blank():
    response = client.post(
        "/ask",
        json={"question": "   "},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "質問を入力してください。"}


def test_ask_returns_no_match_when_question_is_one_character_a():
    response = client.post(
        "/ask",
        json={"question": "あ"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "関連するFAQが見つかりませんでした。",
        "citations": [],
    }


def test_ask_returns_no_match_when_question_is_one_character_i():
    response = client.post(
        "/ask",
        json={"question": "い"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "関連するFAQが見つかりませんでした。",
        "citations": [],
    }


def test_ask_returns_500_when_pdf_file_is_missing(monkeypatch):
    def raise_file_not_found():
        raise FileNotFoundError

    monkeypatch.setattr("app.main.load_document_chunks", raise_file_not_found)

    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "PDFファイルが見つかりません。"}


def test_ask_returns_500_when_pdf_text_cannot_be_extracted(monkeypatch):
    def raise_value_error():
        raise ValueError

    monkeypatch.setattr("app.main.load_document_chunks", raise_value_error)

    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "PDFからテキストを抽出できませんでした。"}


def test_ask_returns_200_when_no_related_faq_is_found():
    response = client.post(
        "/ask",
        json={"question": "まったく関係ない宇宙船の質問"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "関連するFAQが見つかりませんでした。",
        "citations": [],
    }
