# sumiller-bot/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para ChromaDB
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y archivo de configuración
COPY main.py .
COPY config.py .

# Exponer puerto (Cloud Run usará PORT env var)
EXPOSE 8080

# Comando para ejecutar
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]