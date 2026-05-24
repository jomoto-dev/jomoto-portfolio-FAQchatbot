from fastapi import FastAPI
from pydantic import BaseModel

# FastAPIアプリケーションを作成します。
app = FastAPI()


# /ask で受け取るリクエストの形を定義します。
class QuestionRequest(BaseModel):
    question: str


# ヘルスチェック用のエンドポイントです。
@app.get("/health")
def health():
    return {"status": "ok"}


# FAQチャットボットの最小版エンドポイントです。
@app.post("/ask")
def ask(request: QuestionRequest):
    return {
        "answer": "これは最小版の回答です。今後、FAQ文書を検索して回答するように拡張します。",
        "citations": [
            {
                "source": "sample_faq.txt",
                "chunk_id": "chunk_001",
                "text": "これは引用元のサンプルです。",
            }
        ],
    }
