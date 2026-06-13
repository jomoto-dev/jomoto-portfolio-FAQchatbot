from app.services.pdf_loader import split_pdf_text_into_chunks


def test_split_pdf_text_into_chunks_splits_by_article_heading():
    text = """
会社規約サンプル
第1条 返金について
返金は購入から7日以内であれば可能です。
第2条 営業時間について
サポート窓口の営業時間は平日10時から18時までです。
第3条 領収書について
領収書は購入履歴ページからダウンロードできます。
"""

    chunks = split_pdf_text_into_chunks(text)

    assert chunks == [
        "第1条 返金について 返金は購入から7日以内であれば可能です。",
        "第2条 営業時間について サポート窓口の営業時間は平日10時から18時までです。",
        "第3条 領収書について 領収書は購入履歴ページからダウンロードできます。",
    ]


def test_split_pdf_text_into_chunks_falls_back_to_lines():
    text = """
返金は購入から7日以内であれば可能です。
営業時間は平日10時から18時までです。
"""

    chunks = split_pdf_text_into_chunks(text)

    assert chunks == [
        "返金は購入から7日以内であれば可能です。",
        "営業時間は平日10時から18時までです。",
    ]
