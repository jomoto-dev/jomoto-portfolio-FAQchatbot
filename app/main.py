from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.schemas import AskRequest
from app.services.document_loader import load_document_chunks
from app.services.retriever import search_best_chunk

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


# PDFから質問に関連しそうなページを返すエンドポイントです。
@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="質問を入力してください。")

    try:
        chunks = load_document_chunks()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="PDFファイルが見つかりません。")
    except ValueError:
        raise HTTPException(status_code=500, detail="PDFからテキストを抽出できませんでした。")

    result = search_best_chunk(question, chunks)

    if result is None:
        return {
            "answer": "関連するFAQが見つかりませんでした。",
            "citations": [],
        }

    return {
        "answer": result["text"],
        "citations": [
            {
                "source": result["source"],
                "page": result["page"],
                "chunk_id": result["chunk_id"],
                "text": result["text"],
            }
        ],
    }
