FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY . .
EXPOSE 8888

CMD ["python", "python3_app/main.py"]
