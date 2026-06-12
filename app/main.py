from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.schemas import AskRequest
from app.services.document_loader import load_faq_text
from app.services.retriever import search_best_chunk
from app.services.text_splitter import split_into_chunks

# FastAPIアプリケーションを作成します。
app = FastAPI()

INDEX_FILE = Path(__file__).resolve().parent / "static" / "index.html"


# ブラウザ用のチャット画面を返します。
@app.get("/")
def index():
    return FileResponse(INDEX_FILE)


# ヘルスチェック用のエンドポイントです。
@app.get("/health")
def health():
    return {"status": "ok"}


# FAQファイルから質問に関連しそうな段落を返すエンドポイントです。
@app.post("/ask")
def ask(request: AskRequest):
    faq_text = load_faq_text()
    chunks = split_into_chunks(faq_text)
    chunk, index = search_best_chunk(request.question, chunks)

    if chunk is None:
        return {
            "answer": "関連するFAQが見つかりませんでした。",
            "citations": [],
        }

    return {
        "answer": chunk,
        "citations": [
            {
                "source": "sample_faq.txt",
                "chunk_id": f"chunk_{index + 1:03d}",
                "text": chunk,
            }
        ],
    }
