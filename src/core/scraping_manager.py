import requests
from bs4 import BeautifulSoup
from retry import retry
from src.utils.yaml_handler import load_yaml, dump_yaml


class Scraper:
    def __init__(self, case_name: str) -> None:
        _filename_setting = "setting.yml"
        _data_setting = load_yaml(_filename_setting)
        self.data_target = _data_setting["target"][case_name]
        self.base_url = self.data_target["base_url"] + "&page={}"
        self.data_all = []
        self.base_data = {}

    @retry(tries=3, delay=10, backoff=2)
    def _parse_html(self, url: str):
        """
        Parse html from url
        """
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        return soup

    def extract_page(self, page: int) -> dict:
        """
        Extract information in page
        """
        # define url
        url = self.base_url.format(page)
        # get html
        soup = self._parse_html(url)
        # extract all items
        items = soup.findAll("div", {"class": "cassetteitem"})
        print("page", page, "items", len(items))

        # process each item
        for item in items:
            stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
            # process each station
            for station in stations:
                # define variable
                base_data = {}
                # collect base information
                base_data["名称"] = (
                    item.find("div", {"class": "cassetteitem_content-title"})
                    .getText()
                    .strip()
                )
                base_data["カテゴリー"] = (
                    item.find("div", {"class": "cassetteitem_content-label"})
                    .getText()
                    .strip()
                )
                base_data["アドレス"] = (
                    item.find("li", {"class": "cassetteitem_detail-col1"})
                    .getText()
                    .strip()
                )
                base_data["アクセス"] = station.getText().strip()
                base_data["築年数"] = (
                    item.find("li", {"class": "cassetteitem_detail-col3"})
                    .findAll("div")[0]
                    .getText()
                    .strip()
                )
                base_data["構造"] = (
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
                    data = base_data.copy()
                    data["階数"] = tbody.findAll("td")[2].getText().strip()
                    data["家賃"] = (
                        tbody.findAll("td")[3].findAll("li")[0].getText().strip()
                    )
                    data["管理費"] = (
                        tbody.findAll("td")[3].findAll("li")[1].getText().strip()
                    )
                    data["敷金"] = (
                        tbody.findAll("td")[4].findAll("li")[0].getText().strip()
                    )
                    data["礼金"] = (
                        tbody.findAll("td")[4].findAll("li")[1].getText().strip()
                    )
                    data["間取り"] = (
                        tbody.findAll("td")[5].findAll("li")[0].getText().strip()
                    )
                    data["面積"] = (
                        tbody.findAll("td")[5].findAll("li")[1].getText().strip()
                    )
                    data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find(
                        "a"
                    ).get("href")

                    self.data_all.append(data)
