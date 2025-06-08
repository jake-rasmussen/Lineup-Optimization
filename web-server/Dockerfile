# web-server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY web-server/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY web-server .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
