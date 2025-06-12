# sumiller-bot/Dockerfile - CON CONTEXTO DE RAÍZ DEL PROYECTO
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements desde la carpeta sumiller-bot
COPY sumiller-bot/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar archivos de la aplicación
COPY sumiller-bot/main.py .
COPY sumiller-bot/http_client.py .
COPY sumiller-bot/query_filter.py .

# Copiar config.py desde la raíz del proyecto
COPY config.py .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Exponer puerto
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# Comando para ejecutar
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1"]