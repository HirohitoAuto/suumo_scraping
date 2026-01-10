import duckdb
import pandas as pd


def group_by_properties(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """物件をGroup byして重複を排除する
    同じ物件が別IDで登録されており、統計値に与える悪影響を排除するために必要。

    Args:
        df (pd.DataFrame): 物件データのDataFrame
        group_cols (list[str]): Group byするカラム名のリスト
    """
    group_cols_sql = ", ".join(group_cols)
    query = f"""
    with valid_ids as (select min(id) as id from df group by {group_cols_sql})
    select *
    from df
    where id in (select id from valid_ids)
    """
    return duckdb.query(query).to_df()


if __name__ == "__main__":
    filename = "data/fukuoka_convinient/formatted/20260105.csv"
    df = pd.read_csv(filename)
    group_cols = ["price", "age", "layout", "area"]
    df_grouped = group_by_properties(df, group_cols)
    print(f"Before grouping: {len(df)}")
    print(f"After grouping: {len(df_grouped)}")
