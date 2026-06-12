# FAQ RAG Chatbot API


## 概要

FAQ RAG Chatbot API は、FAQテキストをもとにユーザーの質問へ回答し、回答の根拠となる引用元も返す FastAPI 製のWeb APIです。

現在は `data/sample_faq.txt` に登録したFAQを対象に、質問文に関連する段落を簡易検索し、`answer` と `citations` を返します。


本格的なLLM連携やPDF読み込みは未実装ですが、RAGの基本である「文書読み込み → チャンク分割 → 検索 → 引用付き回答返却」の流れを、小さく実装したポートフォリオです。


## デモイメージ


ブラウザからチャット風UIにアクセスし、質問を入力できます。


```text
質問:
返金について教えてください


回答:
返金は購入から7日以内であれば可能です。返金を希望する場合は、お問い合わせフォームから注文番号を送信してください。


引用元:
sample_faq.txt / chunk_001

## 作成背景

Pythonバックエンドエンジニア、特にLLM / NLP 関連の案件を意識し、以下を説明できるポートフォリオとして作成しました。

・FastAPIによるAPI実装
・ファイル読み込みとテキスト処理
・簡易的な検索処理
・引用元付き回答の設計
・pytestによる自動テスト
・機能ごとのファイル分割
・将来的なPDF対応・ベクトル検索・LLM連携への拡張性

## 主な機能

・GET /health によるヘルスチェック
・POST /ask による質問受付
・data/sample_faq.txt の読み込み
・FAQ本文のチャンク分割
・質問文に基づく簡易検索
・回答と引用元の返却
・ブラウザで操作できるチャット風UI
・pytestによるAPIテスト

##使用技術

Python
FastAPI
Uvicorn
Pydantic
pytest
HTML / CSS / JavaScript

## アーキテクチャ

ユーザー
  ↓
チャット風UI
  ↓
POST /ask
  ↓
FastAPI
  ↓
Document Loader
  ↓
Text Splitter
  ↓
Retriever
  ↓
answer + citations

このアプリでは、APIの入口と内部処理を分けています。

・main.py: APIエンドポイント
・schemas.py: リクエスト形式
・services/document_loader.py: FAQテキスト読み込み
・services/text_splitter.py: チャンク分割
・services/retriever.py: 関連チャンク検索

## ディレクトリ構成
faq-rag-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── static/
│   │   └── index.html
│   └── services/
│       ├── __init__.py
│       ├── document_loader.py
│       ├── text_splitter.py
│       └── retriever.py
├── data/
│   └── sample_faq.txt
├── tests/
│   └── test_api.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md

## セットアップ方法

git clone <your-repository-url>
cd faq-rag-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## 起動方法
uvicorn app.main:app --reload

起動後、以下にアクセスします。
http://127.0.0.1:8000/

FastAPIの自動ドキュメントは以下です。
http://127.0.0.1:8000/docs

## 使い方
チャット風UIで質問を入力します。

例:
返金について教えてください

data/sample_faq.txt に関連する内容がある場合、回答と引用元が表示されます。
API仕様
GET /health
アプリが起動しているか確認します。
レスポンス例:
{
  "status": "ok"
}

POST /ask
質問を受け取り、関連するFAQと引用元を返します。
リクエスト例:
{
  "question": "返金について教えてください"
}

レスポンス例:
{
  "answer": "返金は購入から7日以内であれば可能です。返金を希望する場合は、お問い合わせフォームから注文番号を送信してください。",
  "citations": [
    {
      "source": "sample_faq.txt",
      "chunk_id": "chunk_001",
      "text": "返金は購入から7日以内であれば可能です。返金を希望する場合は、お問い合わせフォームから注文番号を送信してください。"
    }
  ]
}

テスト方法
pytest

期待される結果:
3 passed

テストでは、以下を確認しています。
/health が正常に応答すること
/ask が answer と citations を返すこと
/ のチャット風UIが表示できること

## 工夫した点
1. 回答だけでなく引用元を返す設計
LLMや検索APIでは、回答の根拠が分からないと信頼性が下がります。
そのため、answer だけでなく、citations として source, chunk_id, text を返す設計にしました。
2. 小さく動く構成から開始
最初からPDF対応やベクトル検索を入れるのではなく、まずはテキストFAQを対象に、RAGの基本構造を小さく実装しました。
3. 処理を役割ごとに分割
main.py に処理を詰め込まず、読み込み・分割・検索を services/ に分けました。
これにより、今後PDF読み込みやベクトル検索に差し替えやすくしています。
4. pytestによる自動テスト
APIの基本動作をpytestで確認できるようにしました。
今後リファクタリングや機能追加を行っても、基本仕様が壊れていないか確認できます。
5. チャット風UIの追加
FastAPIの /docs だけでなく、ブラウザから質問できる簡単なUIを用意しました。
これにより、APIの動作を非エンジニアにも見せやすくしています。

## 現時点でできること
sample_faq.txt に登録したFAQに基づく回答
回答と引用元の返却
ブラウザからの質問入力
APIドキュメントからの動作確認
pytestによる基本テスト

## 現時点でできないこと
PDFファイルを新規にアップロードして回答すること
複数ファイルを横断した検索
ベクトル検索による意味検索
LLMによる自然文生成
会話履歴を踏まえた回答
ユーザー認証や本番運用向けのログ管理

## 今後の拡張予定
PDF読み込み機能の追加
チャンク分割ロジックの改善
ベクトル検索の導入
LLM APIとの連携
引用元のページ番号表示
エラーハンドリングの強化
Docker対応
GitHub Actionsによる自動テスト

