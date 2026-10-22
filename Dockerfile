FROM python:3.13-slim

WORKDIR /app

# Dependencias del sistema necesarias para Playwright
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Instala Chromium y sus dependencias
RUN playwright install --with-deps chromium

COPY . .

VOLUME ["/app/data"]

EXPOSE 8000

CMD ["sh", "-c", "python init_db.py && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
