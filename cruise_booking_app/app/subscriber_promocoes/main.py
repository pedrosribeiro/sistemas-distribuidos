from app.subscriber_promocoes.consumer import start_consuming

if __name__ == "__main__":
    destino = input("Destino que deseja receber promoções: ")
    start_consuming(destino)
