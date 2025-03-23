import requests
from bs4 import BeautifulSoup
from retry import retry

from src.utils.yaml_handler import load_yaml


class Scraper:
    def __init__(self, case_name: str) -> None:
        _filename_setting = "setting.yml"
        _data_setting = load_yaml(_filename_setting)
        self.data_target = _data_setting["target"][case_name]
        self.base_url = self.data_target["base_url"] + "&page={}"

    def extract_page(self, max_page: int) -> list:
        """
        ページの情報を抽出する
            type: "rental" or "used"
        """
        self.data_all = []
        for page in range(1, max_page + 1):
            print("\npage: ", page)
            url = self.base_url.format(page)
            cnt_items = self._extract_used_page(url)
            if cnt_items == 0:
                break

    @retry(tries=3, delay=10, backoff=2)
    def _parse_html(self, url: str):
        """
        URLのHTMLをパースする
        """
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        return soup

    def _extract_used_page(self, url: str) -> int:
        """
        中古物件ページの情報を抽出する
        """
        soup = self._parse_html(url)
        items = soup.find_all("div", class_="property_unit-content")
        print("items: ", len(items))

        for item in items:
            data_item = {}
            # 物件名
            data_item["name"] = (
                item.find("dd", {"class": "dottable-vm"}).getText().strip()
            )
            # 価格
            data_item["price"] = (
                item.find("span", {"class": "dottable-value"}).getText().strip()
            )
            # 所在地
            dt_tag = item.find("dt", string="所在地")
            if dt_tag:
                data_item["address"] = dt_tag.find_next_sibling("dd").text
            # 沿線・駅
            dt_tag = item.find("dt", string="沿線・駅")
            if dt_tag:
                data_item["access"] = dt_tag.find_next_sibling("dd").text
            # 専有面積
            dt_tag = item.find("dt", string="専有面積")
            if dt_tag:
                data_item["area"] = dt_tag.find_next_sibling("dd").text
            # 間取り
            dt_tag = item.find("dt", string="間取り")
            if dt_tag:
                data_item["layout"] = dt_tag.find_next_sibling("dd").text
            # 築年月
            dt_tag = item.find("dt", string="築年月")
            if dt_tag:
                data_item["yyyymm_construction"] = dt_tag.find_next_sibling("dd").text
            # URL
            a_tag = item.find("a")
            if a_tag:
                data_item["url"] = "https://suumo.jp/" + a_tag["href"]

            self.data_all.append(data_item)
        return len(items)
