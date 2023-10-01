import requests
from bs4 import BeautifulSoup
from retry import retry
from src.utils.yaml_handler import load_yaml, dump_yaml


class Scraper:
    def __init__(self, case_name: str) -> None:
        _filename_setting = "setting.yml"
        _data_setting = load_yaml(_filename_setting)
        self.data_target = _data_setting["target"][case_name]
        self.type = self.data_target["type"]
        self.base_url = self.data_target["base_url"] + "&page={}"

    @retry(tries=3, delay=10, backoff=2)
    def _parse_html(self, url: str):
        """
        URLのHTMLをパースする
        """
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        return soup

    def _extract_rental_page(self, url: str) -> None:
        """
        賃貸物件ページの情報を抽出する
        """
        soup = self._parse_html(url)
        items = soup.findAll("div", {"class": "cassetteitem"})
        # process each item
        for item in items:
            data_item = {}
            stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
            # process each station
            for station in stations:
                # collect base information
                data_item["name"] = (
                    item.find("div", {"class": "cassetteitem_content-title"})
                    .getText()
                    .strip()
                )
                data_item["category"] = (
                    item.find("div", {"class": "cassetteitem_content-label"})
                    .getText()
                    .strip()
                )
                data_item["address"] = (
                    item.find("li", {"class": "cassetteitem_detail-col1"})
                    .getText()
                    .strip()
                )
                data_item["access"] = station.getText().strip()
                data_item["age"] = (
                    item.find("li", {"class": "cassetteitem_detail-col3"})
                    .findAll("div")[0]
                    .getText()
                    .strip()
                )
                data_item["structure"] = (
                    item.find("li", {"class": "cassetteitem_detail-col3"})
                    .findAll("div")[1]
                    .getText()
                    .strip()
                )
                # process for each room
                tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll(
                    "tbody"
                )
                for tbody in tbodys:
                    data = data_item.copy()
                    data["story"] = tbody.findAll("td")[2].getText().strip()
                    data["rent"] = (
                        tbody.findAll("td")[3].findAll("li")[0].getText().strip()
                    )
                    data["management_fee"] = (
                        tbody.findAll("td")[3].findAll("li")[1].getText().strip()
                    )
                    data["deposit"] = (
                        tbody.findAll("td")[4].findAll("li")[0].getText().strip()
                    )
                    data["key_money"] = (
                        tbody.findAll("td")[4].findAll("li")[1].getText().strip()
                    )
                    data["layout"] = (
                        tbody.findAll("td")[5].findAll("li")[0].getText().strip()
                    )
                    data["area"] = (
                        tbody.findAll("td")[5].findAll("li")[1].getText().strip()
                    )
                    data["url"] = "https://suumo.jp" + tbody.findAll("td")[8].find(
                        "a"
                    ).get("href")
                    self.data_all.append(data)

    def _extract_used_page(self, url: str) -> None:
        """
        中古物件ページの情報を抽出する
        """
        soup = self._parse_html(url)
        items = soup.find_all("div", class_="property_unit-content")

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

            self.data_all.append(data_item)

    def extract_page(self, max_page: int) -> list:
        """
        ページの情報を抽出する
            type: "rental" or "used"
        """
        self.data_all = []
        for page in range(1, max_page + 1):
            url = self.base_url.format(page)
            if self.type == "rental":
                self._extract_rental_page(url)
            elif self.type == "used":
                self._extract_used_page(url)
