import os

import duckdb
import pandas as pd
import requests
from bs4 import BeautifulSoup
from retry import retry

from .src.core.formatter import format_data
from .src.utils.geocoder import get_coordinates_from_address
from .src.utils.logger import get_logger
from .src.utils.yaml_handler import load_yaml

logger = get_logger(__name__)


class Scraper:
    def __init__(self, case_name: str) -> None:
        _filename_setting = os.path.join(os.path.dirname(__file__), "setting.yml")
        _data_setting = load_yaml(_filename_setting)
        self.data_target = _data_setting["target"][case_name]
        self.base_url = self.data_target["base_url"] + "&page={}"

    @retry(tries=3, delay=10, backoff=2)
    def _parse_html(self, url: str):
        """URLのHTMLをパースする"""
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        return soup

    def _extract_used_page(self, url: str) -> list:
        """中古物件ページの情報を抽出してリストで返す

        Args:
            url (str): 対象ページのURL

        Returns:
            list: 抽出したデータのリスト
        """
        soup = self._parse_html(url)
        items = soup.find_all("div", class_="property_unit-content")
        logger.debug(f"items: {len(items)}")

        data_page = []
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

            # itemのデータを追加
            data_page.append(data_item)
        return data_page

    def extract_page(self, max_page: int) -> None:
        """全ページの情報を抽出してDataFrameに格納する

        Args:
            max_page (int): 最大ページ数

        Returns:
            None
        """
        data_all_pages = []
        for page in range(1, max_page + 1):
            logger.info(f"page: {page}")
            url = self.base_url.format(page)
            data_page = self._extract_used_page(url)
            if len(data_page) == 0:
                break
            data_all_pages.extend(data_page)
        self.df_lake = pd.DataFrame(data_all_pages)

    def format_data(self) -> None:
        """スクレイピングしたデータを整形したDataFrameを作成する

        Args:
            None

        Returns:
            None
        """
        self.df_formatted = format_data(self.df_lake)

    def remove_replications(self, group_cols: list[str]) -> None:
        """重複物件を排除したDataFrameを作成する
            同じ物件が別IDで登録されており、統計値に与える悪影響を排除するために必要。
        Args:
            group_cols (list[str]): Group byするカラム名のリスト

        Returns:
            None
        """
        df_formatted = self.df_formatted
        group_cols_sql = ", ".join(group_cols)
        query = f"""
        with valid_ids as (select min(id) as id from df_formatted group by {group_cols_sql})
        select *
        from df_formatted
        where id in (select id from valid_ids)
        """
        self.df_grouped = duckdb.query(query).to_df()

    def add_coordinates(self, api_key: str, is_dry_run: bool = False) -> None:
        """住所から緯度・経度を取得してDataFrameに追加する

        Args:
            api_key (str): Google Maps Platform APIキー
            is_dry_run (bool): Dry runモードかどうか

        Returns:
            None
        """
        df = self.df_grouped.copy()

        def get_coordinates_for_row(row):
            """行ごとに緯度・経度を取得する"""
            address = row.get("address", "")
            raw_property_id = row.get("id", None)
            property_id = None
            if pd.notna(raw_property_id) and raw_property_id != "":
                # 正常なIDのみキャッシュキーとして利用できるように正規化
                property_id = str(raw_property_id)
            if pd.notna(address) and isinstance(address, str) and address.strip():
                coordinates = get_coordinates_from_address(
                    address, api_key, property_id
                )
                if coordinates:
                    return pd.Series({"lat": coordinates[0], "lon": coordinates[1]})
                else:
                    logger.warning(f"座標取得失敗: {address}")
                    return pd.Series({"lat": None, "lon": None})
            else:
                logger.warning(f"住所が空です: id={row.get('id', 'unknown')}")
                return pd.Series({"lat": None, "lon": None})

        # 各行に対して緯度・経度を取得
        # Dry runモードの場合はNoneを設定
        if not is_dry_run:
            coordinates_df = df.apply(get_coordinates_for_row, axis=1)
        else:
            coordinates_df = pd.DataFrame(
                {"lat": [None] * len(df), "lon": [None] * len(df)}
            )
        # 緯度・経度カラムを追加
        self.df_mart = df.assign(lat=coordinates_df["lat"], lon=coordinates_df["lon"])
