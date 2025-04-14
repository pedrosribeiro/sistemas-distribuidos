import os

from dotenv import load_dotenv

# Verifica se está rodando em prod ou local
ENV = os.getenv("ENV", "local")

# Escolhe o arquivo correto com base no ambiente
dotenv_path = ".env" if ENV == "prod" else ".env.example"
load_dotenv(dotenv_path)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
