# SUUMO スクレイピング

SUUMO（スーモ）の物件情報をスクレイピングし、データ分析・可視化を行うプロジェクトです。

## 概要

このプロジェクトは以下の機能を提供します：

- **スクレイピング**: SUUMOのWebサイトから物件情報を自動取得
- **データ整形**: 取得したデータをクリーニング・整形
- **分析**: Pythonノートブックによるデータ分析
- **自動実行**: GitHub Actionsによる週次自動スクレイピング

## プロジェクト構造

```
suumo_scraping/
├── .github/              # GitHub Actions ワークフロー
│   └── workflows/
│       ├── weekly-csv-update.yml      # 週次CSVデータ更新
│       ├── daily-gss-update.yml       # 日次Google Spreadsheet更新
│       └── check_spec.yml             # ランナースペック確認
├── scraping/              # スクレイピング関連のコード
│   ├── __main__.py       # メインエントリーポイント
│   ├── scraping_manager.py  # スクレイピング管理
│   ├── setting.yml       # スクレイピング設定
│   ├── data/             # スクレイピング結果データ（CSV）
│   └── src/
│       ├── core/         # コアロジック
│       │   └── formatter.py           # データ整形
│       └── utils/        # ユーティリティ
│           ├── gcp_spreadsheet.py     # GCP Spreadsheet連携
│           └── yaml_handler.py        # YAML設定読込
├── analysis/             # データ分析用ノートブック
│   ├── *.ipynb          # Jupyter Notebook
│   └── chart_meta/      # チャート設定
├── pyproject.toml        # プロジェクト設定とPython依存関係
├── uv.lock              # uvロックファイル
├── Dockerfile           # Dockerイメージ定義
└── Makefile             # Make コマンド定義
```

## セットアップ

### 前提条件

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- GCP認証情報（Google Spreadsheet連携を使用する場合）

### インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd suumo_scraping
```

2. uvのインストール（未インストールの場合）
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. 依存パッケージのインストール
```bash
# プロジェクトルートで実行
uv sync
```

4. GCP認証情報の設定（Google Spreadsheet連携を使用する場合）
```bash
# credentials.jsonをscraping/ディレクトリに配置
cp /path/to/your/credentials.json scraping/credentials.json
```

## `.github/` - GitHub Actions ワークフロー

このリポジトリには以下のGitHub Actionsワークフローが設定されています：

### weekly-csv-update.yml
- **実行タイミング**: 毎週月曜日 1:00 (UTC) / 手動実行可能
- **処理内容**: `fukuoka_convinient` のデータをスクレイピングしCSVファイルとして保存（Google Spreadsheetには反映しない）
- **自動コミット**: CSVデータの更新を自動的にmainブランチにコミット

### daily-gss-update.yml
- **実行タイミング**: 毎日 1:00 (UTC) / 手動実行可能
- **処理内容**: `fukuoka_major_station` のデータをスクレイピングしGoogle Spreadsheetに反映（CSVは保存しない）
- **自動コミット**: なし（Google Spreadsheetのみ更新）

### check_spec.yml
- **実行タイミング**: 手動実行のみ
- **処理内容**: GitHub Actionsランナーのスペック（CPU、メモリ、ディスク、OS）を確認

## `scraping/` - スクレイピング処理

### 処理概要

SUUMOのWebサイトから中古マンション物件情報をスクレイピングし、データを取得・整形・保存します。

**処理フロー**:
1. **データ取得**: 指定されたURLから物件情報をスクレイピング
2. **データ整形**: 取得したデータをクリーニング・型変換
3. **重複除去**: 同じ物件の重複データを排除
4. **保存**: CSVファイルとして保存（オプションでGoogle Spreadsheetにも保存）

**設定ファイル**: `scraping/setting.yml` に各ケース（`fukuoka_convinient`、`fukuoka_major_station`等）の検索条件URLが定義されています。

### 実行方法

#### ローカルで実行する場合

```bash
# 依存パッケージのインストール（プロジェクトルートで実行）
uv sync

# 基本実行（CSVとGoogle Spreadsheetに保存）
uv run python -m scraping <case_name>

# CSVのみ保存（Google Spreadsheet更新をスキップ）
uv run python -m scraping <case_name> --skip-spreadsheet

# Google Spreadsheetのみ更新（CSV保存をスキップ）
uv run python -m scraping <case_name> --skip-csv-storing

# Dry Run（1ページのみスクレイピング、保存なし）
uv run python -m scraping <case_name> --dry-run
```

**利用可能なcase_name**:
- `fukuoka_convinient`: 利便性の高い駅から徒歩15分以内の物件
- `fukuoka_major_station`: 主要駅から徒歩15分以内の物件
- `fukuoka_nov_2024`: その他の検索条件

#### Dockerを使用する場合

```bash
# イメージのビルド
make build

# コンテナの実行（bashシェル起動）
make run

# Dry Runを実行
make dry-run
```

## ダッシュボード
[GoogleSpreadSheetのダッシュボード](https://lookerstudio.google.com/u/0/reporting/6b1b64cb-b655-41ac-8526-28da046e4463/page/piqkF)
