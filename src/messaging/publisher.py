import json
import pika
import os
import time
import logging
from config import log_config

log_config.setup_logging("logs/main_ingestion")
logger = logging.getLogger(__name__)


def publish_message(exchange_name, routing_key, data, retries=3, delay=2):
    connection = None
    for attempt in range(retries):
        try:
            amqp_url = os.environ.get('AMQP_URL')
            if not amqp_url:
                #print("Error: AMQP_URL not set.")
                logger.info("Error: AMQP_URL not set.")
                return False

            url_params = pika.URLParameters(amqp_url)
            connection = pika.BlockingConnection(url_params)
            channel = connection.channel()

            channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

            message = json.dumps(data).encode('utf-8')
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message)

            #print(f"Info sent to '{exchange_name}' with routing key '{routing_key}'.")
            logger.info("Successfully connected")
            logger.info(f"Info sent to '{exchange_name}' with routing key '{routing_key}'.")
            return True

        except pika.exceptions.AMQPConnectionError as e:
            #print(f"[WARN] Connection error (attempt {attempt+1}/{retries}): {e}")
            logger.warning(f"Connection error (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)
        except Exception as e:
            #print(f"[ERROR] Unexpected error: {e}")
            logger.error(f"Unexpected error: {e}")
            return False
        finally:
            if connection and connection.is_open:
                connection.close()
                #print("Connection closed.")
                logger.info("Connection closed.")
    return False

