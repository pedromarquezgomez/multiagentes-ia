# mcp-server/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para ChromaDB
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y archivo de configuración
COPY . .
COPY config.py .

# Copiar archivo de datos de vinos
COPY wines.json .

# Exponer puerto (Cloud Run usará PORT env var)
EXPOSE 8080

# Comando para ejecutar la aplicación con Uvicorn
# Cloud Run proporcionará el puerto a través de la variable PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]