# Dockerfile


FROM python:3.11-slim


WORKDIR /usr/src/app

# 3. Copia primero el fichero de requisitos.
COPY requirements.txt .

# 4. Instala las dependencias del proyecto.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia el resto del código de tu proyecto al directorio de trabajo.
COPY . .