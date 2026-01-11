import os
import sys
from datetime import datetime

import pandas as pd
from dateutil import tz
from src.core.formatter import format_data
from src.core.grouping import group_by_properties
from src.core.scraping_manager import Scraper
from src.utils.gcp_spreadsheet import GcpSpreadSheet

jst = tz.gettz("Asia/Tokyo")
now_jst = datetime.now(jst)
yyyymmdd = int(now_jst.strftime("%Y%m%d"))


def _output_csv(df: pd.DataFrame, dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)
    filename = os.path.join(dir_path, f"{yyyymmdd}.csv")
    df.to_csv(filename, index=False)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scrape.py <case_name>")
        sys.exit(1)
    case_name = sys.argv[1]

    # スクレイピング
    scraper = Scraper(case_name)
    scraper.extract_page(max_page=10000)
    df_raw = pd.DataFrame(scraper.data_all)
    _output_csv(df_raw, f"data/{case_name}/lake")

    # スクレイピング結果を整形
    df_formatted = format_data(df_raw)
    _output_csv(df_formatted.sort_values("id"), f"data/{case_name}/formatted")

    # grouping処理を行う
    df_grouped = group_by_properties(
        df_formatted, group_cols=["name", "price", "age", "layout", "area"]
    )
    _output_csv(df_grouped.sort_values("id"), f"data/{case_name}/grouped")

    # Google Spreadsheetを更新
    spreadsheet = GcpSpreadSheet(
        key="1cg1pxdcvjM4PUjGloCSTGrofmXEWvu_IREJ1SuN5VQY",  # スプレッドシートID
        filename_credentials="credentials.json",
    )
    spreadsheet.dump_dataframe(
        df=df_grouped.sort_values("id"),
        sheet_name="latest",
    )


if __name__ == "__main__":
    main()
