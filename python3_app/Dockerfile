FROM python:3.11-slim

# Логи сразу в stdout
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY . .

EXPOSE 8888

CMD ["python", "main.py"]
