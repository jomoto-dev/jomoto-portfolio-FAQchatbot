from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.schemas import AskRequest
from app.services.llm_client import generate_answer_with_llm
from app.services.pdf_loader import load_pdf_chunks
from app.services.retriever import search_relevant_chunks
from app.state import document_store

# FastAPIアプリケーションを作成します。
app = FastAPI()

INDEX_FILE = Path(__file__).resolve().parent / "static" / "index.html"
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
CURRENT_PDF = UPLOAD_DIR / "current.pdf"


def _build_llm_context(chunks: list[dict]) -> str:
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            "\n".join(
                [
                    f"チャンクID: {chunk['chunk_id']}",
                    f"出典: {chunk['source']}",
                    f"ページ: {chunk['page']}",
                    "本文:",
                    chunk["text"],
                ]
            )
        )

    return "\n\n---\n\n".join(context_parts)


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
    document_store.clear_current_document()

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

    document_store.set_current_document(chunks)

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

    relevant_chunks = search_relevant_chunks(question, chunks, top_k=3)

    if not relevant_chunks:
        return {
            "answer": "関連するPDF本文が見つかりませんでした。",
            "citations": [],
        }

    context = _build_llm_context(relevant_chunks)

    try:
        answer = generate_answer_with_llm(question=question, context=context)
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail="LLM回答生成に失敗しました。APIキーや接続状況を確認してください。",
        )

    return {
        "answer": answer,
        "citations": [
            {
                "source": chunk["source"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
            }
            for chunk in relevant_chunks
        ],
    }
