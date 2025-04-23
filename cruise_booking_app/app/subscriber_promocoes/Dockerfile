FROM python:3.11-slim

WORKDIR /app

COPY app/subscriber_promocoes /app/app/subscriber_promocoes
COPY app/shared              /app/app/shared
COPY app/subscriber_promocoes/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "app/subscriber_promocoes/main.py"]
