import os


SYSTEM_PROMPT = """あなたはPDF文書に基づいて質問に回答するアシスタントです。
必ず以下のPDF抜粋だけを根拠に回答してください。
複数の抜粋がある場合も、PDF抜粋に根拠がない場合は「PDF内に回答の根拠が見つかりませんでした。」と答えてください。
推測や一般知識で補完しないでください。
回答文の中に「【】」「[]」などの引用記号や、不要な括弧・記号を追加しないでください。
引用元はAPI側で別に表示されるため、回答文には引用番号や根拠記号を入れないでください。
回答は日本語で、簡潔に書いてください。"""


def build_llm_context(chunks: list[dict]) -> str:
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


def generate_answer_with_llm(question: str, chunks: list[dict]) -> str:

    try:
        from dotenv import load_dotenv
        from openai import OpenAI
    except Exception as error:
        raise RuntimeError("OpenAI SDKの読み込みに失敗しました。") from error

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEYが設定されていません。")

    context = build_llm_context(chunks)
    user_prompt = f"""質問:
{question}

PDF抜粋:
{context}"""

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )
        answer = response.output_text.strip()
    except Exception as error:
        raise RuntimeError("OpenAI APIで回答生成に失敗しました。") from error

    if not answer:
        raise RuntimeError("OpenAI APIから空の回答が返されました。")

    return answer
