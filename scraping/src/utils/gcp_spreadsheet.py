import logging

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

from .logger import get_logger

logger = get_logger(__name__)


class GcpSpreadSheet:
    def __init__(self, key: str, filename_credentials: str = None):
        # サービスアカウント認証
        creds = Credentials.from_service_account_file(
            f"{filename_credentials}",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        # gspreadでGoogle Sheetsにアクセス
        client = gspread.authorize(creds)
        self.spreadsheet = client.open_by_key(key)

    def dump_dataframe(self, df: pd.DataFrame, sheet_name: str) -> None:
        """DataFrameをスプレッドシートに書き込む

        Args:
            df (pd.DataFrame): 書き込むDataFrame
            sheet_name (str): 書き込むシート名
        """
        worksheet = self.spreadsheet.worksheet(sheet_name)
        # worksheet.clear()

        # 書式を含めてセルをリセット
        self.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "repeatCell": {
                            "range": {"sheetId": worksheet.id},
                            "cell": {},
                            "fields": "*",
                        }
                    }
                ]
            }
        )

        set_with_dataframe(
            worksheet,
            df,
            include_index=False,
            include_column_header=True,
        )
        logger.info(f"DataFrame has been written to sheet '{sheet_name}'.")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"DataFrame head:\n{df.head()}")


if __name__ == "__main__":
    key = "1cg1pxdcvjM4PUjGloCSTGrofmXEWvu_IREJ1SuN5VQY"
    filename_credentials = "../../credentials.json"
    spread_sheet = GcpSpreadSheet(key, filename_credentials)
    filename_data = "../../data/fukuoka_convinient/grouped/20260105.csv"
    df = pd.read_csv(filename_data)
    spread_sheet.dump_dataframe(df, "latest")
