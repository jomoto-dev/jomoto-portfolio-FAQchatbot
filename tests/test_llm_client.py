from app.services.llm_client import build_llm_context


def test_build_llm_context_formats_pdf_chunks_for_llm():
    chunks = [
        {
            "source": "sample_policy_A.pdf",
            "page": 1,
            "chunk_id": "chunk_001",
            "text": "第1条 返金について\n返金は購入から7日以内であれば可能です。",
        },
        {
            "source": "sample_policy_A.pdf",
            "page": 2,
            "chunk_id": "chunk_002",
            "text": "第2条 営業時間について\n営業時間は平日10時から18時までです。",
        },
    ]

    context = build_llm_context(chunks)

    assert "チャンクID: chunk_001" in context
    assert "出典: sample_policy_A.pdf" in context
    assert "ページ: 2" in context
    assert "本文:\n第2条 営業時間について" in context
    assert "\n\n---\n\n" in context
