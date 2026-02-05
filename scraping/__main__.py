import argparse
import os
from datetime import datetime

import pandas as pd
from dateutil import tz

from .scraping_manager import Scraper
from .src.utils.gcp_spreadsheet import GcpSpreadSheet

jst = tz.gettz("Asia/Tokyo")
now_jst = datetime.now(jst)
yyyymmdd = int(now_jst.strftime("%Y%m%d"))
script_dir = os.path.dirname(__file__)


def _output_csv(df: pd.DataFrame, dir_path: str) -> None:
    # 相対パスの場合、スクリプトのディレクトリを基準に解決
    if not os.path.isabs(dir_path):
        dir_path = os.path.join(script_dir, dir_path)

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
    args = parser.parse_args()

    case_name = args.case_name

    scraper = Scraper(case_name)
    scraper.extract_page(max_page=1000)  # スクレイピング
    scraper.format_data()  # スクレイピング結果を整形
    scraper.remove_replications(
        group_cols=["name", "price", "age", "layout", "area"]
    )  # grouping処理を行う

    # 結果データフレームをcsvに保存
    if not args.skip_csv_storing:
        _output_csv(scraper.df_lake, f"data/{case_name}/lake")
        _output_csv(
            scraper.df_formatted.sort_values("id"), f"data/{case_name}/formatted"
        )
        _output_csv(scraper.df_grouped.sort_values("id"), f"data/{case_name}/grouped")

    # Google Spreadsheetを更新
    if not args.skip_spreadsheet:
        print("Updating Google Spreadsheet...")
        # dfにタイムスタンプのカラムを追加
        df_gss = scraper.df_grouped.sort_values("id").copy()
        df_gss["updated_at"] = now_jst.strftime("%Y-%m-%d %H:%M:%S")
        filename_credentials = os.path.join(script_dir, "credentials.json")
        spreadsheet = GcpSpreadSheet(
            key="1cg1pxdcvjM4PUjGloCSTGrofmXEWvu_IREJ1SuN5VQY",  # スプレッドシートID
            filename_credentials=filename_credentials,
        )
        spreadsheet.dump_dataframe(
            df=df_gss,
            sheet_name="latest",
        )


if __name__ == "__main__":
    main()
