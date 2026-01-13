FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar poetry
RUN pip install --no-cache-dir poetry

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock ./

# Configurar poetry para no crear entorno virtual (ya estamos en un contenedor)
RUN poetry config virtualenvs.create false

# Instalar dependencias
RUN poetry install --no-root --no-interaction --no-ansi

# Copiar el código de la aplicación
COPY . .

# Crear directorio para la base de datos
RUN mkdir -p /data

# Script de inicio
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
