# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system packages (for pandas, duckdb etc.)
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Copy project files into container
COPY backend/ backend/
COPY frontend/ frontend/
COPY data/ data/
COPY requirements.txt .
COPY .env .env

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit frontend by default
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
