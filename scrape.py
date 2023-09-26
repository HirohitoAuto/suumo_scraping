import pandas as pd
from src.core.scraping_manager import Scraper


def main():
    """
    suumoのベースURLに対して、ページ番号を変えながらスクレイピングを行う
    """
    scraper = Scraper(case_name)
    for page in range(1, max_page + 1):
        scraper.extract_page(page)
    df_all = pd.DataFrame(scraper.data_all)
    df_all.to_csv(f"result/{case_name}.csv", index=False)


if __name__ == "__main__":
    case_name = "fukuoka"
    max_page = 100
    main()
