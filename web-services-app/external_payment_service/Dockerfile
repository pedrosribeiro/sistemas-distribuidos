FROM python:3.10-slim

WORKDIR /app

COPY external_payment_service.py .

RUN pip install flask requests 

EXPOSE 5050

CMD ["python", "external_payment_service.py"]
