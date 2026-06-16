# FAQ RAG Chatbot API

## 概要

FAQ RAG Chatbot API は、ユーザーがアップロードしたPDFを検索対象にして、質問に関連するPDF抜粋を検索し、その内容を根拠にLLMで回答を生成する FastAPI 製のWeb APIです。

ブラウザのチャット風UIからPDFをアップロードし、そのPDFの内容に対して質問できます。回答本文はOpenAI APIで自然な日本語として生成し、根拠として使ったPDFチャンクは `citations` に残します。

RAGの基本である「文書アップロード → テキスト抽出 → チャンク分割 → 関連チャンク検索 → LLM回答生成 → 引用付き回答返却」の流れを、小さく確認できるポートフォリオです。

## 作成背景

Pythonバックエンドエンジニア、特にLLM / NLP 関連の案件を意識し、以下を説明できるポートフォリオとして作成しました。

- FastAPIによるAPI実装
- PDFアップロード処理
- PDFからのテキスト抽出
- チャンク分割
- 簡易的な検索処理
- OpenAI APIを使ったLLM回答生成
- 引用元付き回答の設計
- pytestによる自動テスト
- 機能ごとのファイル分割
- 将来的なベクトル検索・複数PDF管理への拡張性

## 使用技術

- Python
- FastAPI
- Uvicorn
- Pydantic
- PyMuPDF
- OpenAI Python SDK
- python-dotenv
- python-multipart
- pytest
- HTML / CSS / JavaScript

## API一覧

## デモイメージ

1. ブラウザで `http://127.0.0.1:8000/` を開く
2. PDFを選択してアップロードする
3. 質問を入力する
4. アップロードしたPDFから関連チャンクが検索される
5. PDF抜粋を根拠にしたLLM回答と引用元が表示される

画像追加

## セットアップ方法

```bash
git clone <your-repository-url>
cd faq-rag-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

LLM回答生成を使う場合は、`.env.example` を参考に `.env` を作成し、OpenAI APIキーと使用モデルを設定してください。`.env` はGit管理に含めない前提です。

その後、下記コマンドで起動します

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
規約の同意はどのように成立する？
```

PDFをアップロードしていない状態で質問した場合は、以下のエラーが返ります。

```json
{
  "detail": "先にPDFをアップロードしてください。"
}
```

## 実装した機能

- `GET /health` によるヘルスチェック
- `GET /` によるチャット風UIの表示
- `POST /upload-pdf` によるPDFアップロード
- アップロードPDFの `uploads/current.pdf` への保存
- アップロードPDFからのテキスト抽出
- PDF抽出テキストのクリーニング
- PDF本文の条文・段落単位でのチャンク分割
- 抽出チャンクのメモリ保持
- `POST /ask` による質問受付
- アップロード済みPDFのチャンクに対するキーワード検索
- 関連度が高い複数チャンクの取得
- OpenAI APIを使ったPDF根拠のLLM回答生成
- `answer` と `citations` の返却
- 引用元として `source`, `page`, `chunk_id`, `text` を返す設計
- 回答欄・引用元欄での改行保持表示
- PDFアップロード失敗時に前回PDFの検索状態をクリアする処理
- 空質問、PDF未アップロード、PDF以外のアップロード、抽出失敗へのエラーハンドリング
- pytestによるAPI・PDFローダー・検索処理のテスト

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
LLM Client
  ↓
answer + citations
```

このアプリでは、APIの入口と内部処理を分けています。

- `app/main.py`: APIエンドポイント
- `app/schemas.py`: リクエスト形式
- `app/services/pdf_loader.py`: PDF読み込み・テキスト抽出・チャンク分割
- `app/services/retriever.py`: 関連チャンク検索
- `app/services/llm_client.py`: OpenAI APIによる回答生成
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
│   │   ├── llm_client.py
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
│   ├── sample_policy_A.pdf
│   └── sample_policy_B.pdf
├── tests/
│   ├── test_api.py
│   ├── test_document_loader.py
│   ├── test_pdf_loader.py
│   └── test_retriever.py
├── uploads/
│   └── current.pdf
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

`data/sample_policy_A.pdf`, `data/sample_policy_B.pdf`, `data/sample_faq.txt` はサンプルデータとして残しています。現在の通常フローでは、検索対象はユーザーがアップロードしたPDFです。

・各ファイルの関係性を表した図
<img width="2222" height="1920" alt="Image" src="https://github.com/user-attachments/assets/8629305b-7be3-4fa4-b493-a6b4b024aef1" />

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
  "filename": "sample_policy_A.pdf",
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

質問を受け取り、アップロード済みPDFから関連チャンクを最大3件取得します。取得したPDF抜粋をLLMに渡し、PDF内容に基づく回答文と引用元を返します。

リクエスト例:

```json
{
  "question": "返金について教えてください"
}
```

レスポンス例:

```json
{
  "answer": "購入から7日以内であれば返金可能です。",
  "citations": [
    {
      "source": "sample_policy_A.pdf",
      "page": 1,
      "chunk_id": "chunk_001",
      "text": "第1条 返金について\n返金は購入から7日以内であれば可能です。"
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
23 passed
```

テストでは、以下を確認しています。

- `/health` が正常に応答すること
- `/` のチャット風UIが表示できること
- PDFをアップロードできること
- PDF以外のアップロードが400になること
- PDF未アップロード時の `/ask` が400になること
- アップロード後の `/ask` が `answer` と `citations` を返すこと
- `/ask` が複数の関連チャンクをLLMに渡せること
- LLM呼び出し部分をmonkeypatchし、テストで実APIを呼ばないこと
- 1文字だけの質問が誤ヒットしないこと
- 関連チャンクなしの場合に200で空の `citations` を返すこと
- PDF本文が条文・段落単位で分割されること
- PDF抽出テキストからページ番号らしき単独行を削除できること
- `第18条`, `1ヶ月前`, `7日以内` のような本文中の重要な数字は残ること
- 自然な質問文から関連チャンクを検索できること

## 実装に工夫した点

1. **アップロードPDFを現在の検索対象として扱う設計**

   複数PDF管理やDB保存は入れず、まずは `uploads/current.pdf` とメモリ上の `document_store` に絞りました。これにより、処理の流れをシンプルに保ちながら「アップロードしたPDFに対して質問する」体験を実装しています。

2. **PDF根拠のLLM回答と引用元を分ける設計**

   `answer` はLLMが生成した自然な回答文にし、根拠は `citations` として `source`, `page`, `chunk_id`, `text` を返します。回答文の中に引用記号を混ぜず、根拠確認は引用元欄で行えるようにしています。

3. **条文・段落単位のチャンク分割**

   PDFの1ページ全体を1チャンクにすると、返金・営業時間・領収書など別の話題がまとめて返ってしまいます。そのため、`第1条`, `第2条` のような見出しを区切りにし、見出しがないPDFでも空行や改行で分割するようにしています。

4. **自然な質問文に対応する複数チャンク検索**

   質問文をそのまま文字列一致させるだけでは、`規約の同意はどのように成立する？` のような自然な質問を拾いにくくなります。そのため、意味の薄い語を除外し、`規約`, `同意`, `成立` のような重要語を使ってスコアリングします。関連度が高い最大3件のチャンクをLLMへ渡すことで、回答生成に必要な根拠が届きやすくしています。

5. **PDF抽出テキストのクリーニング**

   PyMuPDFで抽出した本文には、ページ番号やフッターのような行が混ざることがあります。`2` や `- 2 -` のようなページ番号らしき単独行は削除しつつ、`第18条`, `1ヶ月前`, `7日以内` など本文中の数字は消さないようにしています。また、引用元欄で読みやすいように改行を保持しています。

6. **短すぎる質問の誤ヒット防止**

   `"あ"` や `"い"` のような1文字入力が本文中の一部に偶然一致してしまう問題を避けるため、2文字未満の質問や1文字キーワードは検索対象にしないようにしました。

7. **アップロード失敗時に前回PDFを参照しない状態管理**

   新しいPDFアップロードに失敗した場合に、直前に読み込んだPDFのチャンクが残って `/ask` で参照されないよう、アップロード処理開始時に現在の検索状態をクリアします。成功した場合のみ新しいPDFチャンクを検索対象にします。

8. **エラーハンドリングを画面にも表示**

   API側で `HTTPException` を使い、UI側では `detail` を表示します。未アップロード、空質問、PDF以外のアップロード、通信失敗などを利用者に分かりやすく返します。

9. **役割ごとのファイル分割**

   `main.py` に処理を詰め込まず、PDF読み込み、検索、LLM呼び出し、状態管理を別ファイルに分けました。今後、ベクトル検索や複数PDF管理に差し替えるときも変更箇所を追いやすくしています。

## 現時点でできること

- ブラウザからPDFをアップロードする
- アップロードしたPDFを検索対象にする
- PDF本文から条文・段落単位のチャンクを作る
- PDF抽出テキストからページ番号らしき行を取り除く
- 質問に関連する複数チャンクを簡易検索する
- 関連チャンクを根拠にLLMで日本語回答を生成する
- LLM回答と引用元を返す
- 引用元にファイル名、ページ番号、チャンクID、本文を含める
- 回答欄と引用元欄で改行を保持して表示する
- PDFアップロード失敗後に前回PDFを検索対象として残さない
- PDF未アップロードや空質問などのエラーを返す
- pytestで主要なAPI動作を確認する

## 現時点でできないこと

- 複数PDFを同時に管理すること
- サーバー再起動後もアップロード状態を保持すること
- DBにPDFやチャンクを保存すること
- ベクトル検索による意味検索
- 会話履歴を踏まえた回答
- ストリーミング応答
- PDF以外のファイル形式への対応
- ユーザー認証や本番運用向けのログ管理
- OCRが必要なスキャンPDFの高精度な読み取り

## 今後の拡張予定

- 複数PDF管理
- チャンク分割ロジックの改善
- ベクトル検索の導入
- LLM回答の品質改善
- 会話履歴の保持
- Docker対応
- GitHub Actionsによる自動テスト
