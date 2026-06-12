from pydantic import BaseModel


# /ask で受け取るリクエストの形を定義します。
class AskRequest(BaseModel):
    question: str
