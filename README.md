# SUUMO スクレイピング

SUUMO（スーモ）の物件情報をスクレイピングし、データ分析・可視化を行うプロジェクトです。

## 目次

- [概要](#概要)
- [プロジェクト構造](#プロジェクト構造)
- [セットアップ](#セットアップ)
- [GitHub Actions ワークフロー](#github-actions-ワークフロー)
- [スクレイピング処理](#スクレイピング処理)
- [ダッシュボード](#ダッシュボード)

## 概要

SUUMOのWebサイトから物件情報を自動取得し、データ整形・保存を行います。GitHub Actionsで定期実行されます。

## プロジェクト構造

```
suumo_scraping/
├── .github/workflows/    # GitHub Actions ワークフロー
├── scraping/             # スクレイピング関連のコード
│   ├── setting.yml       # スクレイピング設定
│   └── src/              # コアロジック・ユーティリティ
├── Dockerfile
└── Makefile
```

## セットアップ

### 前提条件

- Docker
- GCP認証情報（Google Spreadsheet連携を使用する場合）

### インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd suumo_scraping

# Dockerイメージをビルド
make build
```

GCP認証情報が必要な場合は、`scraping/credentials.json`に配置してください。

## GitHub Actions ワークフロー

### weekly-csv-update.yml
毎週月曜日 1:00 (UTC)に`fukuoka_convinient`をスクレイピングしCSVを保存・コミット

### daily-gss-update.yml
毎日 1:00 (UTC)に`fukuoka_major_station`をスクレイピングしGoogle Spreadsheetを更新

### check_spec.yml
GitHub Actionsランナーのスペック確認（手動実行）

## スクレイピング処理

SUUMOから物件情報を取得し、データ整形・重複除去を行い、CSVまたはGoogle Spreadsheetに保存します。

検索条件は`scraping/setting.yml`に定義されています。

### 実行方法

```bash
# Dockerコンテナ内でスクレイピング実行
make run
# コンテナ内で: uv run python -m scraping <case_name>

# Dry Run（1ページのみスクレイピング）
make dry-run
```

### 利用可能なcase_name

- `fukuoka_convinient`: 利便性の高い駅から徒歩15分以内の物件
- `fukuoka_major_station`: 主要駅から徒歩15分以内の物件
- `fukuoka_nov_2024`: その他の検索条件

### オプション

- `--skip-spreadsheet`: CSVのみ保存
- `--skip-csv-storing`: Google Spreadsheetのみ更新
- `--dry-run`: 1ページのみスクレイピング（保存なし）

## ダッシュボード
[GoogleSpreadSheetのダッシュボード](https://lookerstudio.google.com/u/0/reporting/6b1b64cb-b655-41ac-8526-28da046e4463/page/piqkF)
