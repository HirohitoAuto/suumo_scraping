import os
import sys
from datetime import datetime

import pandas as pd
from dateutil import tz

from src.core.formatter import format_data
from src.core.scraping_manager import Scraper

jst = tz.gettz("Asia/Tokyo")
now_jst = datetime.now(jst)
yyyymmdd = int(now_jst.strftime("%Y%m%d"))


def scrape(case_name: str, max_page: int = 10000) -> pd.DataFrame:
    """suumoのベースURLに対してスクレイピングを行い、結果をcsvファイルに保存する

    Args:
        case_name (str): setting.ymlのtargetに対応するキー
        max_page (int): スクレイピングするページ数

    Returns:
        pd.DataFrame: スクレイピング結果
    """
    scraper = Scraper(case_name)
    scraper.extract_page(max_page)
    return pd.DataFrame(scraper.data_all)


def format(df: pd.DataFrame) -> pd.DataFrame:
    """スクレイピング結果を整形する

    Args:
        df (pd.DataFrame): スクレイピング結果

    Returns:
        pd.DataFrame: 整形後のスクレイピング結果
    """
    return format_data(df)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrape.py <case_name>")
        sys.exit(1)
    case_name = sys.argv[1]

    # スクレイピング
    df_raw = scrape(case_name)
    dir_raw = f"data/{case_name}/lake"
    os.makedirs(dir_raw, exist_ok=True)
    filename_lake = os.path.join(dir_raw, f"lake_{yyyymmdd}.csv")
    df_raw.to_csv(filename_lake, index=False)
    # スクレイピング結果を整形
    df_formatted = format(df_raw)
    dir_formatted = f"data/{case_name}/formatted"
    os.makedirs(dir_formatted, exist_ok=True)
    filename_lake = os.path.join(dir_formatted, f"formatted_{yyyymmdd}.csv")
    df_formatted.to_csv(filename_lake, index=False)
