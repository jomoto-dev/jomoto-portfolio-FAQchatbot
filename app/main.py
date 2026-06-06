from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

# FastAPIアプリケーションを作成します。
app = FastAPI()

# FAQファイルの場所を指定します。
FAQ_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_faq.txt"


# /ask で受け取るリクエストの形を定義します。
class QuestionRequest(BaseModel):
    question: str


# ヘルスチェック用のエンドポイントです。
@app.get("/health")
def health():
    return {"status": "ok"}


def load_faq_paragraphs():
    # FAQ本文を読み込み、空行ごとに段落へ分けます。
    text = FAQ_FILE.read_text(encoding="utf-8")
    return [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]


def extract_keywords(question: str):
    # 質問文から検索に使いやすい短いキーワードを取り出します。
    cleaned = question
    for word in ["について", "教えてください", "教えて", "ください", "ですか", "ますか", "とは"]:
        cleaned = cleaned.replace(word, " ")

    for mark in ["、", "。", "？", "?", "！", "!", "。", ".", ","]:
        cleaned = cleaned.replace(mark, " ")

    return [word.strip(" はをがのにでとも") for word in cleaned.split() if word.strip()]


def find_best_paragraph(question: str, paragraphs: list[str]):
    keywords = extract_keywords(question)
    best_index = -1
    best_score = 0

    for index, paragraph in enumerate(paragraphs):
        score = sum(1 for keyword in keywords if keyword and keyword in paragraph)
        if score > best_score:
            best_index = index
            best_score = score

    if best_score == 0:
        return None, -1

    return paragraphs[best_index], best_index


# FAQファイルから質問に関連しそうな段落を返すエンドポイントです。
@app.post("/ask")
def ask(request: QuestionRequest):
    paragraphs = load_faq_paragraphs()
    paragraph, index = find_best_paragraph(request.question, paragraphs)

    if paragraph is None:
        return {
            "answer": "関連するFAQが見つかりませんでした。",
            "citations": [],
        }

    return {
        "answer": paragraph,
        "citations": [
            {
                "source": "sample_faq.txt",
                "chunk_id": f"chunk_{index + 1:03d}",
                "text": paragraph,
            }
        ],
    }
