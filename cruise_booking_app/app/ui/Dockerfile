FROM python:3.11-slim

WORKDIR /app

# 1) Só traz o requirements da UI e instala
COPY app/ui/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copia apenas o código que a UI precisa
COPY app/ui       /app/app/ui
COPY app/shared   /app/app/shared

# Módulos de reserva usados pela UI
COPY app/ms_reserva/service.py    /app/app/ms_reserva/service.py
COPY app/ms_reserva/publisher.py  /app/app/ms_reserva/publisher.py
COPY app/ms_reserva/data          /app/app/ms_reserva/data

ENV PYTHONPATH=/app

# 3) Entry‑point da UI
CMD ["python", "app/ui/main.py"]
VOLUME ["/app/app/ms_reserva/data"]
