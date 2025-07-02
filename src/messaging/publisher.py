import json
import pika
import os

def publish_message(exchange_name, routing_key, data):
    connection = None
    try:
        # read rabbitmq connection url from environment variable
        amqp_url = os.environ.get('AMQP_URL')
        if not amqp_url:
            print("Error: AMQP_URL not set.")
            return False

        # connect to rabbitmq
        url_params = pika.URLParameters(amqp_url)
        connection = pika.BlockingConnection(url_params)
        channel = connection.channel()

        # Declare Exchange
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

        # Publish message
        message = json.dumps(data).encode('utf-8')
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message)

        print(f"Info sent to '{exchange_name}' with routing key '{routing_key}'.")
        return True

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if connection and connection.is_open:
            connection.close()
            print("Connection closed.")

