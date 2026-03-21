FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entries_server.py .

EXPOSE 8084

# Default port (override via SERVER_PORT env)
CMD ["python", "entries_server.py"]
