import json
import time
import uuid
import pandas as pd
import io
import boto3
import pika
import sys
from dotenv import load_dotenv
import os

def convert_json_to_parquet_buffer(json_data_string):
    try:
        data = json.loads(json_data_string)
        if not data:
            return None
    except json.JSONDecodeError:
        return None

    df = pd.DataFrame(data)
    buffer = io.BytesIO()

    df.to_parquet(buffer, engine='pyarrow', index=False)
    buffer.seek(0)

    return buffer


class S3Consumer:
    """
    Consume messages and store them in a S3 bucket.
    """

    def __init__(self, amqp_url, s3_bucket_name, exchange):
        # El constructor SOLO guarda la configuración. No se conecta.
        self.amqp_url = amqp_url
        self.s3_bucket_name = s3_bucket_name
        self.exchange = exchange
        self.s3_client = boto3.client('s3')
        self.connection = None
        self.channel = None

    def _on_message(self, channel, method, properties, body):
        # No se crea una nueva conexión aquí. Se usa el 'channel' que pika nos da.
        endpoint_name = method.routing_key.split('.')[0]
        print(f"[INFO] Message received for: {endpoint_name}")

        parquet_buffer = convert_json_to_parquet_buffer(body.decode('utf-8'))

        if parquet_buffer:
            s3_key = f"{endpoint_name}/{uuid.uuid4()}.parquet"
            try:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket_name,
                    Key=s3_key,
                    Body=parquet_buffer.getvalue()
                )
                print(f"[INFO] Uploaded to S3[{self.s3_bucket_name}]: {s3_key}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"[ERROR] Error during uploading: {e}")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            print(f"[WARN] Message for {endpoint_name} could not be converted to Parquet. Discarding.")
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self, endpoints_to_consume):
        # Bucle para reintentar la conexión
        max_retries = 5
        retry_delay = 10
        for attempt in range(max_retries):
            try:
                print(f"[INFO] Attempting to connect to RabbitMQ (Attempt {attempt + 1}/{max_retries})...")
                self.connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic')
                print("[INFO] Connection to RabbitMQ successful.")

                for endpoint in endpoints_to_consume:
                    queue_name = endpoint + '_queue'
                    routing_key = endpoint + '.#'
                    self.channel.queue_declare(queue=queue_name, durable=True)
                    self.channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=routing_key)
                    self.channel.basic_consume(
                        queue=queue_name,
                        on_message_callback=self._on_message,
                        auto_ack=False
                    )
                print("[INFO] Waiting for messages...")
                self.channel.start_consuming()
                break  # Sale del bucle si la conexión fue exitosa y se detuvo limpiamente
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[WARN] Connection failed: {e}. Retrying in {retry_delay} seconds...")
                if attempt + 1 == max_retries:
                    print("[ERROR] Max retries reached. Could not connect to RabbitMQ.")
                    break
                time.sleep(retry_delay)
            except Exception as e:
                print(f"[ERROR] An unexpected error occurred: {e}")
                break

        self.stop()

    def stop(self):
        # Detiene el consumo y cierra la conexión de forma segura
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("[INFO] Connection closed.")

if __name__ == '__main__':
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        endpoints_json_path = os.path.join(project_root, 'PBI_endpoints.json')
        with open(endpoints_json_path, 'r') as f:
            ALL_ENDPOINTS = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] file not found  {endpoints_json_path}")
        sys.exit(1)


    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=dotenv_path)

    AMQP_URL = os.getenv('AMQP_URL')
    EXCHANGE_NAME = os.getenv('EXCHANGE_NAME')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

    if not all([AMQP_URL, EXCHANGE_NAME, S3_BUCKET_NAME]):
        raise ValueError("[ERROR] Asegúrate de que AMQP_URL, EXCHANGE_NAME y S3_BUCKET_NAME estén en el .env")

    endpoints_to_process = []
    if len(sys.argv) == 1 or sys.argv[1].lower() == 'all':
        endpoints_to_process = ALL_ENDPOINTS
    elif len(sys.argv) == 2 and sys.argv[1] in ALL_ENDPOINTS:
        endpoints_to_process = [sys.argv[1]]
    else:
        print(f"[ERROR] excpected 1 or 2 arguments but where: '{len(sys.argv[1])}'. Use 'all' or empty to see all endpoints or chose only one")
        sys.exit(1)

    consumer = S3Consumer(AMQP_URL, S3_BUCKET_NAME, EXCHANGE_NAME)
    try:
        print(f"[INFO] Starting : {', '.join(endpoints_to_process)}")
        consumer.run(endpoints_to_process)
    except KeyboardInterrupt:
        print("\n[INFO] Stop by user ctrl+c")
    except Exception as e:
        print(f"[CRITICAL] Unexpected error: {e}")
    finally:
        consumer.stop()

















