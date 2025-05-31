from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import re
import numpy as np
import json
import gc
from typing import Optional, Dict
from io import BytesIO

from backend.llm_agent import generate_sql
from backend.eda_utils import get_basic_eda
from backend.chart_utils import extract_chart_type_from_prompt, infer_chart_type
from backend.sql_runner import run_duckdb_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_schema(df: pd.DataFrame) -> str:
    return "\n".join([f"{col}: {dtype}" for col, dtype in zip(df.columns, df.dtypes)])

def replace_table_names(sql_query: str, target_table: str = "uploaded") -> str:
    pattern = r"\b(FROM|JOIN)\s+(\w+)"
    return re.sub(pattern, lambda m: f"{m.group(1)} {target_table}", sql_query, flags=re.IGNORECASE)

@app.post("/query-file")
async def query_file(prompt: str = Form(...), file: UploadFile = Form(...)):
    try:
        file_bytes = await file.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        df = pd.read_csv(BytesIO(file_bytes))
        schema = extract_schema(df)

        sql_query = generate_sql(prompt, schema)
        sql_query = replace_table_names(sql_query)

        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        for col in numeric_columns:
            sql_query = re.sub(
                rf'"{col}"\s*=\s*\'[ \t]*\'',
                f'TRIM(CAST("{col}" AS TEXT)) = \'\'',
                sql_query
            )

        forbidden_keywords = ["drop", "delete", "update", "insert", "alter"]
        if any(kw in sql_query.lower() for kw in forbidden_keywords):
            return JSONResponse(status_code=400, content={
                "prompt": prompt,
                "sql": sql_query,
                "error": "Query contains forbidden keywords.",
                "retryable": False
            })

        result_df = run_duckdb_query(df, sql_query)
        result_df = result_df.replace([np.inf, -np.inf], np.nan).where(pd.notnull(result_df), None)
        json_ready = json.loads(result_df.to_json(orient="records"))

        forced_chart = extract_chart_type_from_prompt(prompt)
        chart_info = infer_chart_type(sql_query, result_df, forced=forced_chart)

        response_data = {
            "prompt": prompt,
            "sql": sql_query,
            "result": json_ready,
            "chart": chart_info,
        }

        if file_size_mb < 10:
            response_data["eda"] = get_basic_eda(df)

        # Cleanup to reduce memory usage
        del df, result_df
        gc.collect()

        return JSONResponse(content=response_data)

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": f"DuckDB query failed: {str(e)}",
            "retryable": True
        })
