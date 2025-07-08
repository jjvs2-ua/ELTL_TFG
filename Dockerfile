# Dockerfile

# 1. Empieza con una imagen base de Python oficial y ligera.
FROM python:3.11-slim

# 2. Establece el directorio de trabajo dentro del contenedor.
WORKDIR /usr/src/app

# 3. Copia primero el fichero de requisitos.
#    (Esto es una optimización para aprovechar el caché de Docker.
#    Si no cambias las dependencias, este paso no se volverá a ejecutar).
COPY requirements.txt .

# 4. Instala las dependencias del proyecto.
#    --no-cache-dir reduce el tamaño final de la imagen.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia el resto del código de tu proyecto al directorio de trabajo.
COPY . .

# 6. (Opcional) Define el comando por defecto que se ejecutará si no se especifica otro.
#    En tu caso, docker-compose.yml sobrescribe este comando para cada servicio.
CMD ["python", "consumer.py", "all"]