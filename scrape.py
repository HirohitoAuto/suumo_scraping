import pandas as pd

from src.core.formatter import format_data
from src.core.scraping_manager import Scraper
import sys


def scrape_target(case_name: str, max_page: int):
    """
    suumoのベースURLに対して、ページ番号を変えながらスクレイピングを行う
    """
    scraper = Scraper(case_name)
    scraper.extract_page(max_page)
    df = pd.DataFrame(scraper.data_all)
    df_formatted = format_data(df)
    df.to_csv(f"result/{case_name}_raw.csv", index=False)
    df_formatted.to_csv(f"result/{case_name}_formatted.csv", index=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrape.py <case_name> <max_page>")
        sys.exit(1)
    case_name = sys.argv[1]
    max_page = 10000
    scrape_target(case_name, max_page)
