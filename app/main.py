from fastapi import FastAPI

# FastAPIアプリケーションを作成します。
app = FastAPI()


# ヘルスチェック用のエンドポイントです。
@app.get("/health")
def health():
    return {"status": "ok"}
