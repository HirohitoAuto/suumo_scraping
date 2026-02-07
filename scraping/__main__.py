import argparse
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dateutil import tz
from dotenv import load_dotenv

from .scraping_manager import Scraper
from .src.utils.gcp_spreadsheet import GcpSpreadSheet
from .src.utils.logger import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file if it exists
script_dir = Path(__file__).parent
env_path = script_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

jst = tz.gettz("Asia/Tokyo")
now_jst = datetime.now(jst)
yyyymmdd = int(now_jst.strftime("%Y%m%d"))


def _output_csv(df: pd.DataFrame, dir_path: str) -> None:
    # 相対パスの場合、スクリプトのディレクトリを基準に解決
    if not os.path.isabs(dir_path):
        dir_path = str(script_dir / dir_path)

    os.makedirs(dir_path, exist_ok=True)
    filename = os.path.join(dir_path, f"{yyyymmdd}.csv")
    df.to_csv(filename, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape SUUMO data and optionally update Google Spreadsheet"
    )
    parser.add_argument("case_name", help="Case name for scraping")
    parser.add_argument(
        "--skip-spreadsheet",
        action="store_true",
        help="Skip updating Google Spreadsheet",
    )
    parser.add_argument(
        "--skip-csv-storing",
        action="store_true",
        help="Skip storing CSV files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode: scrape only 1 page, skip CSV and Spreadsheet updates",
    )
    args = parser.parse_args()

    case_name = args.case_name

    # Dry runモードの場合、max_page=1に設定
    max_page = 1 if args.dry_run else 1000

    if args.dry_run:
        logger.info("=== DRY RUN MODE ===")
        logger.info("- Scraping only 1 page")
        logger.info("- CSV saving disabled")
        logger.info("- Google Spreadsheet update disabled")
        logger.info("=" * 20)

    scraper = Scraper(case_name)
    scraper.extract_page(max_page=max_page)  # スクレイピング
    scraper.format_data()  # スクレイピング結果を整形
    scraper.remove_replications(
        group_cols=["price", "age", "area", "station_name"]
    )  # grouping処理を行う

    # 緯度・経度を追加してdf_martを作成
    # Dry runモードでない場合のみ実行
    if not args.dry_run:
        google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not google_maps_api_key:
            logger.warning(
                "GOOGLE_MAPS_API_KEY environment variable is not set. "
                "Skipping coordinate geocoding."
            )
        else:
            logger.info("Adding coordinates to data...")
            scraper.add_cordinates(google_maps_api_key)
            # df_martをcsvに保存
            if not args.skip_csv_storing:
                _output_csv(scraper.df_mart.sort_values("id"), f"data/{case_name}/mart")

    # 結果データフレームをcsvに保存
    # Dry runモードの場合はスキップ
    if not args.skip_csv_storing and not args.dry_run:
        _output_csv(scraper.df_lake, f"data/{case_name}/lake")
        _output_csv(
            scraper.df_formatted.sort_values("id"), f"data/{case_name}/formatted"
        )
        _output_csv(scraper.df_grouped.sort_values("id"), f"data/{case_name}/grouped")

    # Google Spreadsheetを更新
    # Dry runモードの場合はスキップ
    if not args.skip_spreadsheet and not args.dry_run:
        logger.info("Updating Google Spreadsheet...")
        # dfにタイムスタンプのカラムを追加
        df_gss = scraper.df_grouped.sort_values("id").copy()
        df_gss["updated_at"] = now_jst.strftime("%Y-%m-%d %H:%M:%S")
        filename_credentials = str(script_dir / "credentials.json")

        # 環境変数からスプレッドシートキーを取得
        spreadsheet_key = os.environ.get("GOOGLE_SPREAD_SHEET_KEY")
        if not spreadsheet_key:
            raise ValueError(
                "GOOGLE_SPREAD_SHEET_KEY environment variable is not set. "
                "Please set it before running this script."
            )

        spreadsheet = GcpSpreadSheet(
            key=spreadsheet_key,
            filename_credentials=filename_credentials,
        )
        spreadsheet.dump_dataframe(
            df=df_gss,
            sheet_name="latest",
        )


if __name__ == "__main__":
    main()
