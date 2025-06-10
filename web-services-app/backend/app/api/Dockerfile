FROM python:3.11-slim

ARG SERVICE_PATH

WORKDIR /app

COPY app /app/app

COPY ${SERVICE_PATH}/ /app/

RUN [ -f requirements.txt ] && pip install --no-cache-dir -r requirements.txt || true

ENV PYTHONPATH="/app/app"

EXPOSE 8000

CMD ["python", "api.py"]
