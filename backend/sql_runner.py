import duckdb
import pandas as pd

def run_duckdb_query(df: pd.DataFrame, sql_query: str, table_name: str = "uploaded") -> pd.DataFrame:
    try:
        con = duckdb.connect()
        con.register(table_name, df)
        result_df = con.execute(sql_query).fetchdf()
        con.close()
        return result_df
    except Exception as e:
        raise RuntimeError(f"DuckDB query failed: {e}")
