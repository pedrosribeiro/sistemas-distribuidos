FROM python:3.11-slim

WORKDIR /app

COPY app/ms_itinerarios /app/app/ms_itinerarios
COPY app/shared /app/app/shared

COPY app/ms_itinerarios/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "app/ms_itinerarios/main.py"]

