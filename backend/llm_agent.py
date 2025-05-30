from openai import OpenAI
from backend.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_sql(prompt, table_schema):
    system_prompt = f"""You are a helpful assistant that generates **raw SQL queries only**, compatible with DuckDB.
Your job is to convert user questions into **pure SQL**, operating on an in-memory table called `uploaded`.

Do NOT:
- Return Python code like `sql("...")`
- Use markdown formatting (e.g., triple backticks)
- Include comments, explanations, or natural language

Only return a clean SQL string like:
SELECT * FROM uploaded LIMIT 5;

Schema:
{table_schema}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    sql = response.choices[0].message.content.strip()

    if "```" in sql:
        sql = sql.split("```")[1].strip()

    return sql
