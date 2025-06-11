# maitre-bot/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY main.py .
COPY firebase_auth.py .

# Puerto que expone Cloud Run
ENV PORT 8000

# Comando para ejecutar
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT