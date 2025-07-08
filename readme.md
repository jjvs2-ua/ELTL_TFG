# 🚀 ETL Pipeline: Business Central a S3

Este proyecto implementa un pipeline de **ETL (Extract, Transform, Load)** robusto y escalable, diseñado para extraer datos de la API de **Microsoft Dynamics 365 Business Central**, transformarlos al formato Parquet y cargarlos en un bucket de **AWS S3**.

Todo el proceso está orquestado con **Docker Compose** y utiliza un bróker de mensajes **RabbitMQ** para desacoplar los servicios y garantizar la fiabilidad en la entrega de datos.

---

## ✨ Características Principales

- **Extracción de Datos Dinámica**: Ingiere datos de múltiples *endpoints* de la API de Business Central, especificados mediante argumentos de línea de comandos.
- **Autenticación Segura**: Utiliza OAuth 2.0 (Client Credentials) para autenticarse de forma segura con la API.
- **Procesamiento Asíncrono**: Emplea **RabbitMQ** como cola de mensajes para gestionar la ingesta de datos de forma asíncrona, mejorando la escalabilidad y la resiliencia.
- **Transformación Eficiente**: Convierte los datos de formato JSON a **Apache Parquet**, optimizando el almacenamiento y la velocidad de las consultas analíticas.
- **Carga en la Nube**: Almacena los archivos Parquet procesados en un bucket de **AWS S3**.
- **Contenerización**: Todo el entorno (aplicación y servicios) está completamente contenerizado con **Docker**, garantizando la portabilidad y la facilidad de despliegue.
- **Logging Centralizado**: Configuración de logging centralizada que guarda los registros en ficheros y silencia el ruido de las librerías de terceros para una depuración más limpia.
- **Configuración Flexible**: Gestiona toda la configuración sensible y de entorno a través de un fichero `.env`.

---

## 🏗️ Arquitectura del Pipeline

El flujo de trabajo se divide en tres componentes principales orquestados por Docker Compose:

1. **Productor (`ingestion_task`)**: Un script de Python (`main_ingestion.py`) que se ejecuta como una tarea. Se encarga de:
   - Obtener un token de autenticación.
   - Realizar peticiones a la API de Business Central para uno o varios *endpoints*.
   - Publicar los datos obtenidos (en formato JSON) en un *exchange* de RabbitMQ.

2. **Bróker de Mensajes (`rabbitmq`)**: Una instancia de RabbitMQ que actúa como intermediario. Recibe los mensajes del productor y los enruta a las colas correspondientes, desacoplando la ingesta de la carga.

3. **Consumidor (`consumer`)**: Un servicio de Python (`consumer.py`) que corre de forma continua. Se encarga de:
   - Escuchar los mensajes de las colas de RabbitMQ.
   - Procesar cada mensaje, convirtiendo los datos JSON a formato Parquet.
   - Subir el fichero `.parquet` resultante al bucket de S3.

```mermaid
graph TD
    A[👨‍💻 Usuario ejecuta Ingestion Task] --> B(main_ingestion.py)
    B --> C{API Business Central}
      --> D[Publica en RabbitMQ]
    subgraph "Docker Compose"
        D -- Mensaje JSON --> E(RabbitMQ Exchange)
        E -- Routing Key --> F[Cola de Endpoint]
        G(consumer.py) -- Escucha --> F
    end
    G --> H(Transforma a Parquet)
    H --> I[☁️ Sube a AWS S3]
```

---

## 📁 Estructura del Proyecto

```
/
├── config/
│   ├── PBI_endpoints.json      # Lista de endpoints de la API a consultar.
│   └── log_config.py           # Módulo de configuración centralizada de logging.
│
├── consumer/
│   └── consumer.py             # Lógica del consumidor: recibe de RabbitMQ, transforma y carga a S3.
│
├── logs/
│   ├── consumer.log            # Logs generados por el consumidor.
│   └── main_ingestion.log      # Logs generados por la tarea de ingesta.
│
├── src/
│   ├── auth/
│   │   └── token_manager.py    # Gestiona la obtención de tokens OAuth 2.0.
│   ├── data_ingestor/
│   │   └── api_cliente.py      # Cliente para realizar peticiones a la API.
│   └── messaging/
│       └── publisher.py        # Publica mensajes en RabbitMQ.
│
├── token/
│   └── token.json              # Almacena el token de acceso más reciente (ignorado por Git).
│
├── .env                        # Fichero de variables de entorno (debe ser creado localmente).
├── docker-compose.yml          # Define y orquesta los servicios de la aplicación.
├── main_ingestion.py           # Punto de entrada para la tarea de ingesta (productor).
└── requirements.txt            # Dependencias de Python del proyecto.
```

---

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha el pipeline en tu entorno local.

### 🔧 Requisitos Previos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 🛠️ Pasos de Instalación

1. **Clona el repositorio:**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_PROYECTO>
    ```

2. **Crea el fichero de entorno `.env`:**

    ```ini
    # .env

    # Credenciales de la App de Microsoft Entra ID (Azure)
    BC_CLIENT_ID="TU_CLIENT_ID"
    BC_CLIENT_SECRET="TU_CLIENT_SECRET"
    BC_TENANT_ID="TU_TENANT_ID"
    BC_BASE_URL="URL_BASE_DE_LA_API_DE_BUSINESS_CENTRAL"

    # Configuración de RabbitMQ
    AMQP_URL="amqp://guest:guest@rabbitmq:5672/"
    EXCHANGE_NAME="API_exchange"

    # Configuración de AWS S3
    S3_BUCKET_NAME="NOMBRE_DE_TU_BUCKET_S3"
    AWS_ACCESS_KEY_ID="TU_AWS_ACCESS_KEY"
    AWS_SECRET_ACCESS_KEY="TU_AWS_SECRET_KEY"
    AWS_DEFAULT_REGION="tu-region-de-aws" # ej: eu-west-1
    ```

3. **Construye y levanta los servicios:**

    ```bash
    docker-compose up -d --build
    ```

    El consumidor (`consumer`) se quedará esperando mensajes.

---

## ▶️ Cómo Usar

Para iniciar la ingesta de datos, ejecuta el servicio `ingestion_task` definido en `docker-compose.yml`.

- **Para ingerir datos de TODOS los *endpoints* definidos en `PBI_endpoints.json`:**

    ```bash
    docker-compose run --rm ingestion_task all
    ```

    *O simplemente:*

    ```bash
    docker-compose run --rm ingestion_task
    ```

- **Para ingerir datos de un ÚNICO *endpoint*:**

    ```bash
    docker-compose run --rm ingestion_task PBI_Bancos
    ```

    *(Reemplaza `PBI_Bancos` por el endpoint que desees procesar).*

Puedes monitorizar los logs de los servicios con:

```bash
# Ver logs del consumidor
docker-compose logs -f consumer

# Ver logs de la tarea de ingesta (mientras se ejecuta)
docker-compose logs -f ingestion_task
```

---

## 📦 Dependencias

Las principales librerías de Python utilizadas en este proyecto son:

- `pika`: Cliente de Python para RabbitMQ.
- `boto3`: SDK de AWS para Python, utilizado para interactuar con S3.
- `pandas`: Para la manipulación y estructuración de datos.
- `pyarrow`: Motor para la escritura de ficheros en formato Parquet.
- `requests`: Para realizar peticiones HTTP a la API.
- `python-dotenv`: Para cargar variables de entorno desde el fichero `.env`.