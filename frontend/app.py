import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import io

st.set_page_config(page_title="LLM Data Analyst", layout="wide")
st.title("🧠 LLM-Powered SQL Analyst")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("""
Welcome to your natural language-powered SQL assistant! Upload a CSV, ask questions in plain English,
and receive SQL queries, charts, and results.
""")

example_prompts = [
    "Show top 5 products by revenue",
    "What are the null counts per column?",
    "Plot average price by category as a bar chart",
    "Give me a histogram of order quantities",
    "Which region has the highest sales?"
]

with st.expander("💡 Need ideas? Click to autofill examples"):
    cols = st.columns(len(example_prompts))
    for i, ex in enumerate(example_prompts):
        if cols[i].button(ex):
            st.session_state["prompt"] = ex

with st.expander("💬 View Past Questions"):
    for i, item in enumerate(st.session_state.chat_history[::-1]):
        st.markdown(f"**Q{i+1}:** {item['prompt']}")
        st.code(item['sql'], language="sql")
        st.caption(f"Result rows: {item['rows']}")

prompt = st.text_input("Ask your data a question:", value=st.session_state.get("prompt", ""), placeholder="e.g., Show me average price by model year")
uploaded_file = st.file_uploader("Upload your CSV dataset", type=["csv"])

def eda_to_markdown(eda: dict) -> str:
    md = f"## EDA Summary\n"
    md += f"**Shape:** {eda['shape']}\n\n"
    md += f"### Null Counts\n"
    for k, v in eda['null_counts'].items():
        md += f"- {k}: {v}\n"
    md += f"\n### Data Types\n"
    for k, v in eda['dtypes'].items():
        md += f"- {k}: {v}\n"
    md += f"\n### Numeric Summary\n"
    for col, stats in eda['numeric_summary'].items():
        md += f"#### {col}\n"
        for metric, value in stats.items():
            md += f"- {metric}: {value}\n"
    md += f"\n### Top Categorical Values\n"
    for col, values in eda['top_values'].items():
        md += f"#### {col}\n"
        for val, count in values.items():
            md += f"- {val}: {count}\n"
    return md

if uploaded_file is not None:
    # Show file size info
    file_size_mb = uploaded_file.size / 1024**2
    st.caption(f"📁 File size: {file_size_mb:.2f} MB")

    if uploaded_file.size > 40 * 1024 * 1024:
        st.error("❌ File too large. Max allowed is 40MB.")
        st.stop()

    try:
        file_id = uploaded_file.name + str(uploaded_file.size)
        if st.session_state.get("last_file_id") != file_id:
            st.session_state["last_file_id"] = file_id
            df_preview = pd.read_csv(uploaded_file, nrows=5)
            st.session_state["df_preview"] = df_preview
    except pd.errors.EmptyDataError:
        st.error("❌ The uploaded file is empty or not a valid CSV.")
        st.stop()

if "df_preview" in st.session_state:
    st.subheader("📄 Preview of Uploaded Data")
    st.dataframe(st.session_state["df_preview"])

if uploaded_file and prompt:
    try:
        df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears empty or corrupted.")
        st.stop()

    with st.spinner("Analyzing and generating SQL..."):
        files = {"file": uploaded_file.getvalue()}
        data = {"prompt": prompt}
        response = requests.post("https://llm-data-analyst-agent.onrender.com/query-file", data=data, files=files)

    if response.status_code == 200:
        result = response.json()
        result_df = pd.DataFrame(result["result"])
        chart_info = result.get("chart")
        eda = result.get("eda")

        st.session_state.chat_history.append({
            "prompt": prompt,
            "sql": result["sql"],
            "chart": result.get("chart"),
            "rows": len(result_df)
        })

        tab1, tab2, tab3 = st.tabs(["📟 SQL Query & Results", "📊 EDA", "📈 Chart"])

        with tab1:
            st.subheader("📟 Generated SQL Query")
            st.code(result["sql"], language="sql")

            st.subheader("📋 Query Result")
            if not result_df.empty:
                if result_df.shape == (1, 1):
                    col_name = result_df.columns[0]
                    value = result_df.iloc[0, 0]
                    st.success(f"**{col_name.replace('_', ' ').capitalize()}: {value}**")
                else:
                    st.dataframe(result_df)

                    st.download_button(
                        "⬇️ Download Query Result as CSV",
                        result_df.to_csv(index=False).encode("utf-8"),
                        "query_results.csv",
                        "text/csv"
                    )

                    excel_buf = io.BytesIO()
                    result_df.to_excel(excel_buf, index=False, engine='xlsxwriter')
                    excel_buf.seek(0)
                    st.download_button(
                        "⬇️ Download Query Result as Excel",
                        excel_buf,
                        "query_results.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("Query returned no data.")

        with tab2:
            st.subheader("📊 Basic EDA Summary")
            if eda:
                st.write(f"**Shape:** {eda['shape']}")
                st.write("**Null Counts:**")
                st.json(eda["null_counts"])
                st.write("**Data Types:**")
                st.json(eda["dtypes"])
                st.write("**Numeric Summary:**")
                st.json(eda["numeric_summary"])
                st.write("**Top Categorical Values:**")
                st.json(eda["top_values"])
                st.write("**Data Preview:**")
                st.dataframe(eda["preview"])

                eda_md = eda_to_markdown(eda)
                st.download_button("📄 Download EDA Summary (Markdown)", eda_md, "eda_summary.md", "text/markdown")

                cleaned_df = df.dropna()
                st.download_button("⬇️ Download Cleaned Dataset", cleaned_df.to_csv(index=False).encode("utf-8"), "cleaned_data.csv", "text/csv")
            else:
                if uploaded_file.size > 10 * 1024 * 1024:
                    st.info("📦 EDA skipped for large file (>10MB).")
                else:
                    st.warning("No EDA summary returned.")

        with tab3:
            st.subheader("📈 Visualization")
            if chart_info:
                chart_type = chart_info.get("chart_type")
                if chart_type == "bar":
                    st.bar_chart(result_df.set_index(chart_info["x"])[chart_info["y"]])
                elif chart_type == "pie":
                    fig = px.pie(result_df, names=chart_info["labels"], values=chart_info["values"])
                    st.plotly_chart(fig)
                elif chart_type == "line":
                    fig = px.line(result_df, x=chart_info["x"], y=chart_info["y"])
                    st.plotly_chart(fig)
                elif chart_type == "scatter":
                    fig = px.scatter(result_df, x=chart_info["x"], y=chart_info["y"])
                    st.plotly_chart(fig)
                elif chart_type == "histogram":
                    fig = px.histogram(result_df, x=chart_info["x"])
                    st.plotly_chart(fig)
                elif chart_type == "box":
                    fig = px.box(result_df, x=chart_info["x"], y=chart_info["y"])
                    st.plotly_chart(fig)
                else:
                    st.info("Chart type not yet supported.")
            else:
                st.info("No chart generated from this query.")
    else:
        try:
            error_msg = response.json().get("error", "Unknown error")
            retryable = response.json().get("retryable", False)
            st.error(f"❌ Backend error: {error_msg}")
            if retryable:
                if st.button("🔁 Try Again"):
                    response = requests.post("https://llm-data-analyst-agent.onrender.com/query-file", data=data, files=files)
                    st.rerun()
        except Exception:
            st.error("Something went wrong and the backend did not return JSON.")
