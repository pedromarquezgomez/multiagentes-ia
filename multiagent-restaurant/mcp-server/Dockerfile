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

# Copiar código fuente
COPY . .

# Copiar archivo de datos de vinos
COPY wines.json .

# Exponer puerto
EXPOSE 8002

# Puerto que espera Cloud Run
ENV PORT=8002

# Comando para ejecutar la aplicación con Uvicorn.
# Cloud Run utilizará el $PORT definido en la variable de entorno anterior.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]