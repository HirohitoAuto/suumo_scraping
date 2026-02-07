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

### GCP認証情報の設定（オプション）

Google Spreadsheet連携を使用する場合は、`scraping/credentials.json`に認証情報を配置してください。

### Google Maps API設定（座標取得機能を使用する場合）

物件の住所から緯度・経度を取得する機能を使用する場合は、Google Maps Platform APIキーが必要です。

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Geocoding APIを有効化
3. APIキーを作成
4. 環境変数に設定：
   ```bash
   export GOOGLE_MAPS_API_KEY="your_api_key_here"
   ```
   または、`scraping/.env`ファイルに記載：
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

この機能により、`data/{case_name}/mart/`ディレクトリに緯度（`lat`）・経度（`lon`）カラムを含む`df_mart`が保存されます。

## GitHub Actions ワークフロー

| ワークフロー | 実行タイミング | 処理内容 |
|---|---|---|
| weekly-csv-update.yml | 毎週月曜日 1:00 (UTC) | `fukuoka_convinient`をスクレイピングしCSVを保存・コミット |
| daily-gss-update.yml | 毎日 1:00 (UTC) | `main_disttricts`をスクレイピングしGoogle Spreadsheetを更新 |
| check_spec.yml | 手動実行 | GitHub Actionsランナーのスペック確認 |

## スクレイピング処理

SUUMOから物件情報を取得し、データ整形・重複除去を行い、CSVまたはGoogle Spreadsheetに保存します。

検索条件は`scraping/setting.yml`に定義されています。

### 実行方法

```bash
# Dockerコンテナを起動してbashシェルに入る
make run

# コンテナ内で以下を実行
uv run python -m scraping <case_name>
```

または、Dry Runで動作確認：
```bash
make dry-run
```

### 利用可能なcase_name

- `fukuoka_convinient`: 利便性の高い駅から徒歩15分以内の物件
- `main_disttricts`: 福岡市+春日市+大野城市で、駅から徒歩20分以内の物件
- `fukuoka_nov_2024`: その他の検索条件

### オプション

- `--skip-spreadsheet`: CSVのみ保存
- `--skip-csv-storing`: Google Spreadsheetのみ更新
- `--dry-run`: 1ページのみスクレイピング（保存なし）

### 出力データ

スクレイピング処理は以下のデータセットを生成します：

- `data/{case_name}/lake/`: 生のスクレイピング結果
- `data/{case_name}/formatted/`: 整形済みデータ
- `data/{case_name}/grouped/`: 重複除去済みデータ
- `data/{case_name}/mart/`: 緯度・経度情報を含むデータ（`GOOGLE_MAPS_API_KEY`が設定されている場合のみ）

## ダッシュボード
[GoogleSpreadSheetのダッシュボード](https://lookerstudio.google.com/u/0/reporting/6b1b64cb-b655-41ac-8526-28da046e4463/page/piqkF)
