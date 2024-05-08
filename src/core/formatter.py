import datetime
import pandas as pd


class Formatter:

    def format_used(self, df: pd.DataFrame) -> pd.DataFrame:
        # 金額
        df["price"] = df["price"].str.replace("億円", "0000")
        df["price"] = df["price"].str.replace("万", "")
        df["price"] = df["price"].str.replace("億", "")
        df["price"] = df["price"].str.replace("円", "")
        df["price"] = df["price"].astype(int)
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

        colums = [
            "name",
            "price",
            "line",
            "station_name",
            "minutes",
            "area",
            "layout",
            "age",
            "address",
            "url",
        ]
        df_formatted = df[colums]
        return df_formatted
