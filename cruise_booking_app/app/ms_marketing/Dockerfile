FROM python:3.11-slim

WORKDIR /app

COPY app/ms_marketing /app/app/ms_marketing
COPY app/shared       /app/app/shared
COPY app/ms_marketing/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "app/ms_marketing/main.py"]
