FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# зависимости
COPY python3_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY python3_app/ .
EXPOSE 8888

CMD ["python", "main.py"]
