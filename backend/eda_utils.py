import pandas as pd

def get_basic_eda(df: pd.DataFrame) -> dict:
    eda_result = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe(include='number').round(2).to_dict(),
        "preview": df.head(5).to_dict(orient="records")
    }
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    eda_result["top_values"] = {
        col: df[col].value_counts().head(5).to_dict() for col in cat_cols
    }
    return eda_result
