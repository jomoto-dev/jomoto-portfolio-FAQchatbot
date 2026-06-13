# FAQ RAG Chatbot API

## 概要

FAQ RAG Chatbot API は、ユーザーがアップロードしたPDFを検索対象にして、質問に関連する本文チャンクと引用元を返す FastAPI 製のWeb APIです。

ブラウザのチャット風UIからPDFをアップロードし、そのPDFの内容に対して質問できます。回答はLLMで生成するのではなく、PDFから抽出した関連チャンクをそのまま返します。

RAGの基本である「文書アップロード → テキスト抽出 → チャンク分割 → 検索 → 引用付き回答返却」の流れを、小さく確認できるポートフォリオです。

## デモイメージ

1. ブラウザで `http://127.0.0.1:8000/` を開く
2. PDFを選択してアップロードする
3. 質問を入力する
4. アップロードしたPDFから関連チャンクと引用元が表示される

```text
質問:
返金について教えてください

回答:
第1条 返金について 返金は購入から7日以内であれば可能です。

引用元:
sample_policy.pdf / page 1 / chunk_001
```

## 実装した機能

- `GET /health` によるヘルスチェック
- `GET /` によるチャット風UIの表示
- `POST /upload-pdf` によるPDFアップロード
- アップロードPDFの `uploads/current.pdf` への保存
- アップロードPDFからのテキスト抽出
- PDF本文の条文・段落単位でのチャンク分割
- 抽出チャンクのメモリ保持
- `POST /ask` による質問受付
- アップロード済みPDFのチャンクに対する簡易検索
- `answer` と `citations` の返却
- 引用元として `source`, `page`, `chunk_id`, `text` を返す設計
- 空質問、PDF未アップロード、PDF以外のアップロード、抽出失敗へのエラーハンドリング
- pytestによるAPI・PDFローダーのテスト

## 作成背景

Pythonバックエンドエンジニア、特にLLM / NLP 関連の案件を意識し、以下を説明できるポートフォリオとして作成しました。

- FastAPIによるAPI実装
- PDFアップロード処理
- PDFからのテキスト抽出
- チャンク分割
- 簡易的な検索処理
- 引用元付き回答の設計
- pytestによる自動テスト
- 機能ごとのファイル分割
- 将来的なベクトル検索・LLM連携への拡張性

## 使用技術

- Python
- FastAPI
- Uvicorn
- Pydantic
- PyMuPDF
- python-multipart
- pytest
- HTML / CSS / JavaScript

## アーキテクチャ

```text
ユーザー
  ↓
チャット風UI
  ↓
POST /upload-pdf
  ↓
FastAPI
  ↓
PDF Loader
  ↓
Document Store
  ↓
POST /ask
  ↓
Retriever
  ↓
answer + citations
```

このアプリでは、APIの入口と内部処理を分けています。

- `app/main.py`: APIエンドポイント
- `app/schemas.py`: リクエスト形式
- `app/services/pdf_loader.py`: PDF読み込み・テキスト抽出・チャンク分割
- `app/services/retriever.py`: 関連チャンク検索
- `app/state/document_store.py`: アップロード済みPDFのチャンクをメモリ上に保持
- `app/static/index.html`: チャット風UI

## ディレクトリ構成

```text
faq-rag-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_loader.py
│   │   ├── pdf_loader.py
│   │   ├── retriever.py
│   │   └── text_splitter.py
│   ├── state/
│   │   ├── __init__.py
│   │   └── document_store.py
│   └── static/
│       └── index.html
├── data/
│   ├── sample_faq.txt
│   └── sample_policy.pdf
├── tests/
│   ├── test_api.py
│   ├── test_document_loader.py
│   └── test_pdf_loader.py
├── uploads/
│   └── current.pdf
├── pyproject.toml
├── requirements.txt
└── README.md
```

`data/sample_policy.pdf` と `data/sample_faq.txt` はサンプルデータとして残しています。現在の通常フローでは、検索対象はユーザーがアップロードしたPDFです。

## セットアップ方法

```bash
git clone <your-repository-url>
cd faq-rag-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動方法

```bash
uvicorn app.main:app --reload
```

起動後、以下にアクセスします。

- チャット風UI: <http://127.0.0.1:8000/>
- FastAPI 自動ドキュメント: <http://127.0.0.1:8000/docs>

## 使い方

1. チャット風UIを開く
2. `PDFをアップロード` からPDFファイルを送信する
3. アップロード成功後、PDFの内容に関する質問を入力する

質問例:

```text
返金について教えてください
営業時間について教えてください
領収書について教えてください
```

PDFをアップロードしていない状態で質問した場合は、以下のエラーが返ります。

```json
{
  "detail": "先にPDFをアップロードしてください。"
}
```

## API仕様

### `GET /health`

アプリが起動しているか確認します。

レスポンス例:

```json
{
  "status": "ok"
}
```

### `POST /upload-pdf`

PDFをアップロードし、抽出したチャンクを現在の検索対象としてメモリ上に保存します。

リクエスト形式:

```text
multipart/form-data
file: PDFファイル
```

レスポンス例:

```json
{
  "message": "PDFをアップロードしました。",
  "filename": "sample_policy.pdf",
  "chunk_count": 3
}
```

PDF以外をアップロードした場合:

```json
{
  "detail": "PDFファイルをアップロードしてください。"
}
```

PDFからテキストを抽出できない場合:

```json
{
  "detail": "PDFからテキストを抽出できませんでした。"
}
```

### `POST /ask`

質問を受け取り、アップロード済みPDFから関連チャンクと引用元を返します。

リクエスト例:

```json
{
  "question": "返金について教えてください"
}
```

レスポンス例:

```json
{
  "answer": "第1条 返金について 返金は購入から7日以内であれば可能です。",
  "citations": [
    {
      "source": "sample_policy.pdf",
      "page": 1,
      "chunk_id": "chunk_001",
      "text": "第1条 返金について 返金は購入から7日以内であれば可能です。"
    }
  ]
}
```

関連チャンクが見つからない場合:

```json
{
  "answer": "関連するFAQが見つかりませんでした。",
  "citations": []
}
```

空質問の場合:

```json
{
  "detail": "質問を入力してください。"
}
```

## テスト方法

```bash
pytest
```

期待される結果:

```text
16 passed
```

テストでは、以下を確認しています。

- `/health` が正常に応答すること
- `/` のチャット風UIが表示できること
- PDFをアップロードできること
- PDF以外のアップロードが400になること
- PDF未アップロード時の `/ask` が400になること
- アップロード後の `/ask` が `answer` と `citations` を返すこと
- 1文字だけの質問が誤ヒットしないこと
- 関連チャンクなしの場合に200で空の `citations` を返すこと
- PDF本文が条文・段落単位で分割されること

## 実装に工夫した点

1. **アップロードPDFを現在の検索対象として扱う設計**

   複数PDF管理やDB保存は入れず、まずは `uploads/current.pdf` とメモリ上の `document_store` に絞りました。これにより、処理の流れをシンプルに保ちながら「アップロードしたPDFに対して質問する」体験を実装しています。

2. **回答だけでなく引用元を返す設計**

   回答の根拠を確認できるように、`answer` だけでなく `citations` として `source`, `page`, `chunk_id`, `text` を返します。アップロード元ファイル名も `source` に残るため、どのPDFのどこから返答されたか確認できます。

3. **条文・段落単位のチャンク分割**

   PDFの1ページ全体を1チャンクにすると、返金・営業時間・領収書など別の話題がまとめて返ってしまいます。そのため、`第1条`, `第2条` のような見出しを区切りにし、見出しがないPDFでも空行や改行で分割するようにしています。

4. **短すぎる質問の誤ヒット防止**

   `"あ"` や `"い"` のような1文字入力が本文中の一部に偶然一致してしまう問題を避けるため、2文字未満の質問や1文字キーワードは検索対象にしないようにしました。

5. **エラーハンドリングを画面にも表示**

   API側で `HTTPException` を使い、UI側では `detail` を表示します。未アップロード、空質問、PDF以外のアップロード、通信失敗などを利用者に分かりやすく返します。

6. **役割ごとのファイル分割**

   `main.py` に処理を詰め込まず、PDF読み込み、検索、状態管理を別ファイルに分けました。今後、ベクトル検索やLLM連携に差し替えるときも変更箇所を追いやすくしています。

## 現時点でできること

- ブラウザからPDFをアップロードする
- アップロードしたPDFを検索対象にする
- PDF本文から条文・段落単位のチャンクを作る
- 質問に関連するチャンクを簡易検索する
- 回答と引用元を返す
- 引用元にファイル名、ページ番号、チャンクID、本文を含める
- PDF未アップロードや空質問などのエラーを返す
- pytestで主要なAPI動作を確認する

## 現時点でできないこと

- 複数PDFを同時に管理すること
- サーバー再起動後もアップロード状態を保持すること
- DBにPDFやチャンクを保存すること
- ベクトル検索による意味検索
- LLMによる自然文生成
- 会話履歴を踏まえた回答
- PDF以外のファイル形式への対応
- ユーザー認証や本番運用向けのログ管理

## 今後の拡張予定

- 複数PDF管理
- チャンク分割ロジックの改善
- ベクトル検索の導入
- LLM APIとの連携
- 会話履歴の保持
- Docker対応
- GitHub Actionsによる自動テスト
