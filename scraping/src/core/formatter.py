import datetime
import re

import pandas as pd


def format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    scrapingしたデータを整形する
    """

    # 金額
    def parse_price(price_str):
        price_str = price_str.replace("円", "")
        # 「億」の値を取得
        oku_match = re.search(r"(\d+(?:\.\d+)?)億", price_str)
        oku = float(oku_match.group(1)) if oku_match else 0
        # 「万」の値を取得
        man_match = re.search(r"(\d+(?:\.\d+)?)万", price_str)
        man = float(man_match.group(1)) if man_match else 0
        # 合計を万単位で計算
        total = oku * 10000 + man
        return int(total)

    df["price"] = df["price"].apply(parse_price)
    # 路線・駅・徒歩
    df["station_name"] = df["access"].str.extract("「(.*?)」")
    df["line"] = df["access"].str.split("「", expand=True)[0]
    df["minutes"] = df["access"].str.extract(r"徒歩(.*?)分")
    # 面積m2
    df["area"] = df["area"].str.extract(r"(\d+(?:\.\d+)?)m2")
    # 築年数
    df["yyyymm"] = pd.to_datetime(df["yyyymm_construction"], format="%Y年%m月")
    current_year = datetime.datetime.now().year
    df["age"] = current_year - df["yyyymm"].dt.year
    # 型変換
    df.dropna(subset=["price", "minutes", "area", "age"], inplace=True)
    df["price"] = df["price"].astype(int)
    df["minutes"] = df["minutes"].astype(int)
    df["area"] = df["area"].astype(float)
    df["age"] = df["age"].astype(int)
    # idの付与 urlの末尾からidを取得
    df["id"] = df["url"].apply(
        lambda x: re.search(r"nc_(\d+)/", x).group(1) if isinstance(x, str) else None
    )
    colums = [
        "id",
        "name",
        "price",
        "age",
        "line",
        "station_name",
        "minutes",
        "layout",
        "area",
        "address",
        "url",
    ]
    df_formatted = df[colums]
    return df_formatted
