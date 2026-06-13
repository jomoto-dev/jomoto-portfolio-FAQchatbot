from fastapi.testclient import TestClient

from app.main import app
from app.state import document_store


# FastAPIアプリをテスト用クライアントで呼び出します。
client = TestClient(app)


def upload_sample_pdf():
    with open("data/sample_policy.pdf", "rb") as pdf_file:
        return client.post(
            "/upload-pdf",
            files={"file": ("sample_policy.pdf", pdf_file, "application/pdf")},
        )


def assert_no_match_response(response):
    assert response.status_code == 200
    assert response.json() == {
        "answer": "関連するFAQが見つかりませんでした。",
        "citations": [],
    }


def setup_function():
    document_store.clear_current_document()


def teardown_function():
    document_store.clear_current_document()


def test_index_returns_ok():
    response = client.get("/")

    assert response.status_code == 200


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_pdf_returns_message_and_chunk_count():
    response = upload_sample_pdf()

    assert response.status_code == 200
    assert response.json() == {
        "message": "PDFをアップロードしました。",
        "filename": "sample_policy.pdf",
        "chunk_count": 3,
    }


def test_upload_pdf_returns_400_when_file_is_not_pdf():
    response = client.post(
        "/upload-pdf",
        files={"file": ("sample.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "PDFファイルをアップロードしてください。"}


def test_ask_returns_400_when_pdf_is_not_uploaded():
    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "先にPDFをアップロードしてください。"}


def test_ask_returns_answer_and_citations():
    upload_response = upload_sample_pdf()
    assert upload_response.status_code == 200

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
    upload_response = upload_sample_pdf()
    assert upload_response.status_code == 200

    response = client.post(
        "/ask",
        json={"question": "あ"},
    )

    assert_no_match_response(response)


def test_ask_returns_no_match_when_question_is_one_character_i():
    upload_response = upload_sample_pdf()
    assert upload_response.status_code == 200

    response = client.post(
        "/ask",
        json={"question": "い"},
    )

    assert_no_match_response(response)


def test_upload_pdf_returns_400_when_text_cannot_be_extracted(monkeypatch):
    def raise_value_error(pdf_path, source_name=None):
        raise ValueError

    monkeypatch.setattr("app.main.load_pdf_chunks", raise_value_error)

    response = upload_sample_pdf()

    assert response.status_code == 400
    assert response.json() == {"detail": "PDFからテキストを抽出できませんでした。"}


def test_ask_returns_200_when_no_related_faq_is_found():
    upload_response = upload_sample_pdf()
    assert upload_response.status_code == 200

    response = client.post(
        "/ask",
        json={"question": "まったく関係ない宇宙船の質問"},
    )

    assert_no_match_response(response)
