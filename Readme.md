# 🧠 LLM-Powered Data Analyst Agent

A smart, interactive analytics tool that lets users query datasets using natural language. Powered by OpenAI and DuckDB, it transforms English questions into SQL, executes them, and returns insights with visualizations — all in a clean Streamlit interface.

---

## 🚀 Features

- 🔍 **Natural Language to SQL** — Ask questions like “Show top 5 products by revenue” or “Which region has highest sales?”
- 📊 **Charts on Demand** — Generates bar, line, pie, histogram, scatter, and box plots.
- 📁 **CSV Uploads** — Analyze any CSV file without code.
- 🧠 **Automated EDA** — Instant summary of missing values, basic stats, and column types.
- 💡 **Prompt Suggestions** — Example questions for quick exploration.
- 🧼 **Error Handling** — Graceful feedback for invalid queries or empty results.
- 🔁 **Retry Support** — Intelligent fallback when SQL execution fails.

---

## 🛠️ How It Works

This project bridges natural language and structured data analysis using LLMs and SQL. Here's the step-by-step breakdown:

### 1. 🔁 User Interaction (Frontend)
- The user uploads a CSV and enters a prompt in natural language via **Streamlit UI**.
- Example prompt: *"Show top 5 products by revenue"*

### 2. 📄 Schema Extraction
- The backend reads the uploaded CSV using **Pandas**.
- It dynamically extracts the schema (column names and types) to provide context to the LLM.

### 3. 🤖 Prompt Engineering & LLM Integration
- The extracted schema and user prompt are sent to **OpenAI** (GPT-4 or GPT-3.5).
- The LLM generates an SQL query that matches the user's intent and the data schema.

### 4. 🦆 SQL Execution with DuckDB
- The SQL query is executed in-memory using **DuckDB** on the uploaded dataset.
- Results are returned as a DataFrame for preview and visualization.

### 5. 📈 Chart Rendering
- If the user’s prompt implies a chart (bar, line, pie, etc.), a matching chart type is inferred using rule-based parsing.
- A Plotly chart is rendered based on the SQL result.

### 6. 🧠 EDA Summary
- On every upload, a quick EDA summary is generated using `eda_utils.py`.
- This includes: column types, missing values, value counts, and basic statistics.

### 7. 🔄 Retry and Validation
- If the LLM-generated SQL fails or is malformed, a fallback message is shown with optional retry logic.
- Basic keyword checks are used to avoid destructive queries (e.g., DROP, DELETE).

---

## 📂 Project Structure

```
llm-data-analyst-agent/
│
├── backend/
│   ├── main.py              # FastAPI app with /query-file endpoint
│   ├── llm_agent.py         # Converts prompt + schema into SQL using OpenAI
│   ├── eda_utils.py         # Generates EDA summaries
│   ├── chart_utils.py       # Extracts chart type from prompt
│   └── sql_runner.py        # (Optional) Extra SQL tools or validation
│
├── frontend/
│   └── app.py               # Streamlit UI
│
├── data/
│   └── ecommerce.csv        # Sample dataset
│
├── requirements.txt
└── README.md
```

---

## 💻 How to Run

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/llm-data-analyst-agent.git
cd llm-data-analyst-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload
```

### 4. Start the Frontend (Streamlit)

Open a new terminal:

```bash
cd frontend
streamlit run app.py
```

---

## 🔐 Environment Variables

`llm_agent.py` currently uses a hardcoded OpenAI key. Update this for production.

```python
# Replace with your actual API key in llm_agent.py
OPENAI_API_KEY = "your-api-key"
```

---

## ✨ Demo Prompts

Try these in the app:

- "Show top 5 products by revenue"
- "Plot sales by category as a bar chart"
- "What are the null counts per column?"
- "Give me a histogram of order quantities"
- "Which region has the highest sales?"

---

## 📦 To-Do & Upcoming

- [ ] 📥 Download SQL results or EDA summary
- [ ] 🧠 Session memory for follow-up questions
- [ ] 📝 Export EDA report as PDF
- [ ] 📊 KPI dashboard generation
- [ ] 🔐 Secure OpenAI key via environment variables
- [ ] ☁️ Deploy to Streamlit Cloud or Hugging Face Spaces

---

## 📜 License

MIT License. See `LICENSE` file for details.

---

## 👨‍💻 Author

**Saksham Tyagi**  
📍 Arlington, Texas  
📧 [sakshamtyagi134@gmail.com](mailto:sakshamtyagi134@gmail.com)  
🔗 [LinkedIn](https://linkedin.com/in/sakshamtyagi)

---
