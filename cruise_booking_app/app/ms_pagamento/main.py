import logging

from app.ms_pagamento.consumer import start_consuming

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

if __name__ == "__main__":
    logging.info("[MS Pagamento] Iniciando...")
    start_consuming()
