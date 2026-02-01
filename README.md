# SUUMO スクレイピング

SUUMO（スーモ）の物件情報をスクレイピングし、データ分析・可視化を行うプロジェクトです。

## 概要

このプロジェクトは以下の機能を提供します：

- **スクレイピング**: SUUMOのWebサイトから物件情報を自動取得
- **データ整形**: 取得したデータをクリーニング・整形
- **分析**: Pythonノートブックによるデータ分析
- **可視化**: Streamlitを使った対話型ダッシュボード

## プロジェクト構造

```
suumo_scraping/
├── scraping/              # スクレイピング関連のコード
│   ├── scrape.py         # メインのスクレイピングスクリプト
│   ├── requirements.txt   # Python依存関係
│   ├── setting.yml       # スクレイピング設定
│   ├── credentials.json  # GCP認証情報
│   └── src/
│       ├── core/         # コアロジック
│       │   ├── scraping_manager.py    # スクレイピング管理
│       │   ├── formatter.py           # データ整形
│       │   └── grouping.py            # データグループ化
│       └── utils/        # ユーティリティ
│           ├── gcp_spreadsheet.py     # GCP Spreadsheet連携
│           └── yaml_handler.py        # YAML設定読込
│   └── data/             # スクレイピングデータ保存先
│       ├── airport_line/
│       ├── fukuoka_convinient/
│       └── nanakuma/
├── streamlit/            # Streamlitダッシュボード
│   ├── app.py           # メインアプリケーション
│   └── requirements.txt
├── analysis/            # Jupyter ノートブック
│   ├── airport_line.ipynb
│   ├── fukuoka_nov_2024.ipynb
│   └── nanakuma.ipynb
├── Dockerfile.scraping
├── Dockerfile.streamlit
├── Makefile
└── README.md
```

## セットアップ

### 前提条件

- Docker & Docker Compose
- Python 3.8以上
- GCP認証情報（Google Spreadsheet連携を使用する場合）

### インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd suumo_scraping
```

2. 環境変数を設定（必要に応じて）
```bash
export CASE_NAME="福岡_便利"
```

## 使用方法

### スクレイピングの実行

#### Dockerを使用する場合（推奨）

```bash
# イメージのビルド
make build_scraping

# コンテナの実行
make run_scraping

# コンテナ内でスクレイピング実行
python scrape.py <case_name> 
```

## ダッシュボード
[GoogleSpreadSheetのダッシュボード](https://lookerstudio.google.com/u/0/reporting/6b1b64cb-b655-41ac-8526-28da046e4463/page/piqkF)
