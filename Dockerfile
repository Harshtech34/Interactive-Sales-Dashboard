# Use official Python slim
FROM python:3.11-slim

WORKDIR /app

# system deps for matplotlib (fonts)
RUN apt-get update && apt-get install -y build-essential libglib2.0-0 libsm6 libxrender1 libxext6 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed DB at build time (optional)
RUN python src/seed_data.py

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
