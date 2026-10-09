FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx python-multipart

COPY . .

EXPOSE 8000

CMD ["python", "-m", "finaudit.cli", "serve"]
