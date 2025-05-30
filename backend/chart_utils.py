from typing import Optional, Dict

def extract_chart_type_from_prompt(prompt: str) -> Optional[str]:
    p = prompt.lower()
    if "pie chart" in p: return "pie"
    if "bar chart" in p or "bar graph" in p: return "bar"
    if "line chart" in p or "line graph" in p: return "line"
    if "scatter" in p: return "scatter"
    if "histogram" in p: return "histogram"
    if "box plot" in p or "boxplot" in p: return "box"
    return None

def infer_chart_type(sql_query: str, df, forced: Optional[str] = None) -> Optional[Dict]:
    if df.empty or len(df.columns) < 1:
        return None
    cols = df.columns.tolist()
    types = df.dtypes

    if forced == "pie" and len(cols) >= 2:
        return {"chart_type": "pie", "labels": cols[0], "values": cols[1]}
    if forced == "bar" and len(cols) >= 2:
        return {"chart_type": "bar", "x": cols[0], "y": cols[1]}
    if forced == "line" and len(cols) >= 2:
        return {"chart_type": "line", "x": cols[0], "y": cols[1]}
    if forced == "scatter" and len(cols) >= 2:
        return {"chart_type": "scatter", "x": cols[0], "y": cols[1]}
    if forced == "histogram":
        return {"chart_type": "histogram", "x": cols[0]}
    if forced == "box" and len(cols) >= 2:
        return {"chart_type": "box", "x": cols[0], "y": cols[1]}

    if "group by" in sql_query.lower() and len(cols) >= 2:
        return {"chart_type": "bar", "x": cols[0], "y": cols[1]}
    if len(cols) == 2 and types[cols[1]] in ['int64', 'float64']:
        return {"chart_type": "pie", "labels": cols[0], "values": cols[1]}
    return None
