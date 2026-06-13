from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.schemas import AskRequest
from app.services.pdf_loader import load_pdf_chunks
from app.services.retriever import search_best_chunk
from app.state import document_store

# FastAPIアプリケーションを作成します。
app = FastAPI()

INDEX_FILE = Path(__file__).resolve().parent / "static" / "index.html"
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
CURRENT_PDF = UPLOAD_DIR / "current.pdf"


# ブラウザ用のチャット画面を返します。
@app.get("/")
def index():
    return FileResponse(INDEX_FILE)


# ヘルスチェック用のエンドポイントです。
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDFファイルをアップロードしてください。")

    filename = Path(file.filename or "uploaded.pdf").name

    try:
        UPLOAD_DIR.mkdir(exist_ok=True)
        content = await file.read()
        CURRENT_PDF.write_bytes(content)
    except OSError:
        raise HTTPException(status_code=500, detail="PDFの保存に失敗しました。")

    try:
        chunks = load_pdf_chunks(CURRENT_PDF, source_name=filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="PDFからテキストを抽出できませんでした。")
    except Exception:
        raise HTTPException(status_code=400, detail="PDFからテキストを抽出できませんでした。")

    document_store.set_current_document(chunks, filename)

    return {
        "message": "PDFをアップロードしました。",
        "filename": filename,
        "chunk_count": len(chunks),
    }


# アップロード済みPDFから質問に関連しそうなチャンクを返すエンドポイントです。
@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="質問を入力してください。")

    chunks = document_store.get_current_chunks()
    if not chunks:
        raise HTTPException(status_code=400, detail="先にPDFをアップロードしてください。")

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
