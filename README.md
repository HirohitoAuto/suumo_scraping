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
│       ├── scrape-and-commit.yml      # 週次スクレイピング＆コミット
│       └── check_spec.yml             # ランナースペック確認
├── scraping/              # スクレイピング関連のコード
│   ├── __main__.py       # メインエントリーポイント
│   ├── scraping_manager.py  # スクレイピング管理
│   ├── requirements.txt   # Python依存関係
│   ├── setting.yml       # スクレイピング設定
│   ├── credentials.json  # GCP認証情報
│   └── src/
│       ├── core/         # コアロジック
│       │   └── formatter.py           # データ整形
│       └── utils/        # ユーティリティ
│           ├── gcp_spreadsheet.py     # GCP Spreadsheet連携
│           └── yaml_handler.py        # YAML設定読込
├── analysis/            # Jupyter ノートブック
├── Dockerfile.scraping
└── Makefile
```

## セットアップ

### 前提条件

- Python 3.11以上
- GCP認証情報（Google Spreadsheet連携を使用する場合）

### インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd suumo_scraping
```

2. 依存パッケージのインストール
```bash
cd scraping
pip install -r requirements.txt
```

3. GCP認証情報の設定（Google Spreadsheet連携を使用する場合）
```bash
# credentials.jsonをscraping/ディレクトリに配置
cp /path/to/your/credentials.json scraping/credentials.json
```

## `.github/` - GitHub Actions ワークフロー

このリポジトリには以下のGitHub Actionsワークフローが設定されています：

### weekly-csv-update.yml
- **実行タイミング**: 毎週月曜日 0:00 (UTC) / 手動実行可能
- **処理内容**: `fukuoka_convinient` のデータをスクレイピングしCSVファイルとして保存（Google Spreadsheetには反映しない）
- **自動コミット**: CSVデータの更新を自動的にmainブランチにコミット

### scrape-and-commit.yml
- **実行タイミング**: 毎週月曜日 0:00 (UTC) / 手動実行可能
- **処理内容**: 
  - `fukuoka_convinient`: CSVのみ保存
  - `fukuoka_major_station`: CSVとGoogle Spreadsheetに保存
- **自動コミット**: CSVデータの更新を自動的にmainブランチにコミット

### check_spec.yml
- **実行タイミング**: pushまたは手動実行
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
# 依存パッケージのインストール
cd scraping
pip install -r requirements.txt

# 基本実行（CSVとGoogle Spreadsheetに保存）
python -m scraping <case_name>

# CSVのみ保存（Google Spreadsheet更新をスキップ）
python -m scraping <case_name> --skip-spreadsheet

# Google Spreadsheetのみ更新（CSV保存をスキップ）
python -m scraping <case_name> --skip-csv-storing
```

**利用可能なcase_name**:
- `fukuoka_convinient`: 利便性の高い駅から徒歩15分以内の物件
- `fukuoka_major_station`: 主要駅から徒歩15分以内の物件
- `fukuoka_nov_2024`: その他の検索条件

#### Dockerを使用する場合

```bash
# イメージのビルド
make build_scraping

# コンテナの実行
make run_scraping

# コンテナ内でスクレイピング実行
python -m scraping <case_name>
```

## ダッシュボード
[GoogleSpreadSheetのダッシュボード](https://lookerstudio.google.com/u/0/reporting/6b1b64cb-b655-41ac-8526-28da046e4463/page/piqkF)
