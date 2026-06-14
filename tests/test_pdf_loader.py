from app.services.pdf_loader import clean_extracted_text, split_pdf_text_into_chunks


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
        "第1条 返金について\n返金は購入から7日以内であれば可能です。",
        "第2条 営業時間について\nサポート窓口の営業時間は平日10時から18時までです。",
        "第3条 領収書について\n領収書は購入履歴ページからダウンロードできます。",
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


def test_clean_extracted_text_removes_page_number_lines_only():
    text = """
2
第18条（中途解約）
利用者が契約期間中に解約を希望する場合、解約希望月の1ヶ月前までに通知するものとします。
- 3 -
返金は購入から7日以内であれば可能です。
"""

    cleaned = clean_extracted_text(text)

    assert "\n2\n" not in f"\n{cleaned}\n"
    assert "- 3 -" not in cleaned
    assert "第18条（中途解約）" in cleaned
    assert "1ヶ月前" in cleaned
    assert "7日以内" in cleaned


def test_clean_extracted_text_normalizes_spaces_and_blank_lines():
    text = "  第1条   返金について  \n\n\n  返金は   購入から7日以内です。  "

    cleaned = clean_extracted_text(text)

    assert cleaned == "第1条 返金について\n\n返金は 購入から7日以内です。"
