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
