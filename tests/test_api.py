import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app
from app.state import document_store


# FastAPIアプリをテスト用クライアントで呼び出します。
client = TestClient(app)


def upload_sample_pdf():
    with open("data/sample_policy_A.pdf", "rb") as pdf_file:
        return client.post(
            "/upload-pdf",
            files={"file": ("sample_policy_A.pdf", pdf_file, "application/pdf")},
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


@pytest.fixture(autouse=True)
def use_temporary_upload_path(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(main, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(main, "CURRENT_PDF", upload_dir / "current.pdf")


def fake_generate_answer_with_llm(question: str, context: str) -> str:
    return "LLMによるテスト回答です。"


def sample_policy_b_chunks():
    return [
        {
            "source": "sample_policy_B.pdf",
            "page": 1,
            "chunk_id": "chunk_001",
            "text": "第1条（目的） 本規約は、当社が提供する本サービスの利用に関する基本的な事項を定めることを目的とします。",
        },
        {
            "source": "sample_policy_B.pdf",
            "page": 1,
            "chunk_id": "chunk_002",
            "text": "第2条（規約の同意） 利用者は、本サービスの利用を申し込んだ時点で、本規約のすべての内容に同意したものとみなします。",
        },
        {
            "source": "sample_policy_B.pdf",
            "page": 1,
            "chunk_id": "chunk_003",
            "text": "第3条（規約の変更） 当社は、必要と判断した場合、本規約を変更できるものとします。",
        },
    ]


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
        "filename": "sample_policy_A.pdf",
        "chunk_count": 3,
    }


def test_upload_pdf_returns_400_when_file_is_not_pdf():
    response = client.post(
        "/upload-pdf",
        files={"file": ("sample.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "PDFファイルをアップロードしてください。"}


def test_upload_pdf_failure_clears_previous_pdf(monkeypatch):
    monkeypatch.setattr("app.main.generate_answer_with_llm", fake_generate_answer_with_llm)

    upload_response = upload_sample_pdf()
    assert upload_response.status_code == 200

    answer_response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )
    assert answer_response.status_code == 200
    assert answer_response.json()["answer"] == "LLMによるテスト回答です。"

    failed_upload_response = client.post(
        "/upload-pdf",
        files={"file": ("sample.txt", b"hello", "text/plain")},
    )
    assert failed_upload_response.status_code == 400

    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "先にPDFをアップロードしてください。"}


def test_ask_returns_400_when_pdf_is_not_uploaded():
    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "先にPDFをアップロードしてください。"}


def test_ask_returns_answer_and_citations(monkeypatch):
    monkeypatch.setattr("app.main.generate_answer_with_llm", fake_generate_answer_with_llm)

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
    assert data["answer"] == "LLMによるテスト回答です。"
    assert data["citations"]

    citation = data["citations"][0]
    assert set(citation) == {"source", "page", "chunk_id", "text"}
    assert citation["source"] == "sample_policy_A.pdf"
    assert citation["page"] == 1
    assert citation["chunk_id"] == "chunk_001"
    assert "返金" in citation["text"]


def test_ask_sends_multiple_relevant_chunks_to_llm(monkeypatch):
    captured = {}

    def fake_generate_answer(question: str, context: str) -> str:
        captured["question"] = question
        captured["context"] = context
        return "規約の同意に関するテスト回答です。"

    monkeypatch.setattr("app.main.generate_answer_with_llm", fake_generate_answer)
    document_store.set_current_document(sample_policy_b_chunks(), "sample_policy_B.pdf")

    response = client.post(
        "/ask",
        json={"question": "規約の同意はどのように成立する？"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["answer"] == "規約の同意に関するテスト回答です。"
    assert [citation["chunk_id"] for citation in data["citations"]] == [
        "chunk_002",
        "chunk_001",
        "chunk_003",
    ]
    assert captured["question"] == "規約の同意はどのように成立する？"
    assert "チャンクID: chunk_002" in captured["context"]
    assert "ページ: 1" in captured["context"]
    assert "規約の同意" in captured["context"]


def test_ask_returns_500_when_llm_generation_fails(monkeypatch):
    def raise_runtime_error(question: str, context: str) -> str:
        raise RuntimeError

    monkeypatch.setattr("app.main.generate_answer_with_llm", raise_runtime_error)

    upload_response = upload_sample_pdf()
    assert upload_response.status_code == 200

    response = client.post(
        "/ask",
        json={"question": "返金について教えてください"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "LLM回答生成に失敗しました。APIキーや接続状況を確認してください。"
    }


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
