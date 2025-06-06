import pika


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost", credentials=pika.PlainCredentials("admin", "admin")
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="hello")

    channel.basic_publish(exchange="", routing_key="hello", body="Hello World!")
    logging.info(" [x] Sent 'Hello World!'")
    connection.close()


if __name__ == "__main__":
    main()
