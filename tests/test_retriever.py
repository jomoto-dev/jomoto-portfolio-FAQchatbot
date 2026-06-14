from app.services.retriever import search_relevant_chunks


def test_search_relevant_chunks_finds_policy_agreement_from_natural_question():
    chunks = [
        {
            "source": "sample_policy_B.pdf",
            "page": 1,
            "chunk_id": "chunk_001",
            "text": "第1条（目的） 本規約は、本サービスの利用に関する基本的な事項を定めることを目的とします。",
        },
        {
            "source": "sample_policy_B.pdf",
            "page": 1,
            "chunk_id": "chunk_002",
            "text": "第2条（規約の同意） 利用者は、本サービスの利用を申し込んだ時点で、本規約のすべての内容に同意したものとみなします。",
        },
        {
            "source": "sample_policy_B.pdf",
            "page": 1,
            "chunk_id": "chunk_003",
            "text": "第3条（規約の変更） 当社は、必要と判断した場合、本規約を変更できるものとします。",
        },
    ]

    results = search_relevant_chunks("規約の同意はどのように成立する？", chunks)

    assert results
    assert results[0]["chunk_id"] == "chunk_002"
    assert any(chunk["chunk_id"] == "chunk_002" for chunk in results)


def test_search_relevant_chunks_returns_empty_for_one_character_question():
    chunks = [
        {
            "source": "sample_policy_A.pdf",
            "page": 1,
            "chunk_id": "chunk_001",
            "text": "第1条 返金について 返金は購入から7日以内であれば可能です。",
        }
    ]

    assert search_relevant_chunks("あ", chunks) == []
