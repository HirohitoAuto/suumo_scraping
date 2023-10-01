import pandas as pd
from src.core.scraping_manager import Scraper


def scrape_target(case_name: str, max_page: int):
    """
    suumoのベースURLに対して、ページ番号を変えながらスクレイピングを行う
    """
    scraper = Scraper(case_name)
    scraper.extract_page(max_page)
    df_all = pd.DataFrame(scraper.data_all)
    df_all.to_csv(f"result/{case_name}.csv", index=False)


if __name__ == "__main__":
    case_name = "福岡_used"
    max_page = 100
    scrape_target(case_name, max_page)
