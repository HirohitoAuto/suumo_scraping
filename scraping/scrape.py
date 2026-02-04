import argparse
import os
from datetime import datetime

import pandas as pd
from dateutil import tz
from scraping_manager import Scraper
from src.utils.gcp_spreadsheet import GcpSpreadSheet

jst = tz.gettz("Asia/Tokyo")
now_jst = datetime.now(jst)
yyyymmdd = int(now_jst.strftime("%Y%m%d"))


def _output_csv(df: pd.DataFrame, dir_path: str) -> None:
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
    args = parser.parse_args()

    case_name = args.case_name

    # スクレイピング
    scraper = Scraper(case_name)
    scraper.extract_page(max_page=1000)
    _output_csv(scraper.df_lake, f"data/{case_name}/lake")

    # スクレイピング結果を整形
    scraper.format_data()
    _output_csv(scraper.df_formatted.sort_values("id"), f"data/{case_name}/formatted")

    # grouping処理を行う
    scraper.remove_replications(group_cols=["name", "price", "age", "layout", "area"])
    _output_csv(scraper.df_grouped.sort_values("id"), f"data/{case_name}/grouped")

    # Google Spreadsheetを更新
    if not args.skip_spreadsheet:
        print("Updating Google Spreadsheet...")
        spreadsheet = GcpSpreadSheet(
            key="1cg1pxdcvjM4PUjGloCSTGrofmXEWvu_IREJ1SuN5VQY",  # スプレッドシートID
            filename_credentials="credentials.json",
        )
        spreadsheet.dump_dataframe(
            df=scraper.df_grouped.sort_values("id"),
            sheet_name="latest",
        )


if __name__ == "__main__":
    main()
