FROM python:3.11-slim

WORKDIR /app

COPY app /app/app
COPY app/ms_reserva/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "app/ms_reserva/main.py"]
