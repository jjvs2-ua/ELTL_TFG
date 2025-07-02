import json
import pandas as pd
import io
import boto3
import pika

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
    def __init__(self, amqp_url, s3_bucket_name):
        self.amqp_url = amqp_url
        self.s3_bucket_name = s3_bucket_name

    def _on_message(self, channel, method, properties, body):
        body = body.decode('utf-8')
        data = convert_json_to_parquet_buffer(body)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.s3_bucket_name)
        bucket.put_object(Key='', Body=data)


    def run(self, endpoints_to_consume): # Inicia la conexión y el bucle infinito para escuchar mensajes.
        # read rabbitmq connection url from environment variable
        amqp_url = self.amqp_url
        url_params = pika.URLParameters(amqp_url)

        # connect to rabbitmq
        connection = pika.BlockingConnection(url_params)
        channel = connection.channel()

        # declare exchange
        channel.exchange_declare(exchange='API_exchange', exchange_type='topic')
        # Declare Queue
        queue_name = QUEUE_ARG[field]
        channel.queue_declare(queue=queue_name)
        # bind queue
        routing_key = field + '.#'
        channel.queue_bind(exchange='API_exchange', queue=queue_name, routing_key=routing_key)
        # consume
        channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=customers_on_message_callback)

        print("Waiting to consume")
        # start consuming
        channel.start_consuming()

    def stop(self): # Detiene el consumo y cierra la conexión de forma segura.
        pass

if __name__ == '__main__':
    # 1. Configurar y procesar los argumentos de la línea de comandos ('all' o un endpoint).


    # 2. Decidir qué colas escuchar en base al argumento recibido.


    # 3. Cargar la configuración necesaria desde las variables de entorno (URLs, bucket, etc.).


    # 4. Crear la instancia del consumidor y ponerlo en marcha de forma segura.
