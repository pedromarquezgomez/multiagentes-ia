#!/bin/bash
# start-railway.sh - Script de inicio para Railway

set -e

echo "🚀 Iniciando Sistema Sumiller en Railway..."

# Configurar variables de entorno predeterminadas
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}
export PYTHONPATH="/app:$PYTHONPATH"

# Crear directorios necesarios
mkdir -p /app/data /app/logs /app/.chromadb

# Verificar API keys obligatorias
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: Se requiere OPENAI_API_KEY"
    exit 1
fi

echo "✅ Usando OPENAI_API_KEY configurada"

# Configurar URLs por defecto si no están definidas
export RAG_MCP_URL=${RAG_MCP_URL:-"http://localhost:8000"}
export MEMORY_MCP_URL=${MEMORY_MCP_URL:-"http://localhost:8002"}

# Log de configuración
echo "📊 Configuración:"
echo "  - Puerto: $PORT"
echo "  - Entorno: $ENVIRONMENT"
echo "  - API Base URL: $OPENAI_BASE_URL"
echo "  - Modelo: $OPENAI_MODEL"

# Función para esperar a que un servicio esté listo
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Esperando a que $service_name esté listo..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url/health" > /dev/null 2>&1; then
            echo "✅ $service_name está listo"
            return 0
        fi
        
        echo "  Intento $attempt/$max_attempts - $service_name no está listo..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "⚠️  WARNING: $service_name no respondió en tiempo esperado"
    return 1
}

# Inicializar base de datos si es necesario
if [ -f "/app/load-wines.py" ]; then
    echo "📚 Cargando base de conocimientos de vinos..."
    cd /app && python load-wines.py || echo "⚠️  No se pudo cargar la base de vinos (continuando...)"
fi

# Función para iniciar el servidor principal
start_main_server() {
    echo "🍷 Iniciando Sumiller Bot en puerto $PORT..."
    cd /app
    exec uvicorn sumiller-bot.main:app \
        --host 0.0.0.0 \
        --port "$PORT" \
        --log-level info \
        --access-log \
        --loop uvloop \
        --http h11
}

# Función para cleanup al recibir señales
cleanup() {
    echo "🛑 Deteniendo servicios..."
    # Aquí podrías agregar cleanup adicional si es necesario
    exit 0
}

# Capturar señales para cleanup
trap cleanup SIGTERM SIGINT

# Verificar health del sistema
health_check() {
    if curl -s -f "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo "✅ Sistema funcionando correctamente"
        return 0
    else
        echo "❌ Error en health check"
        return 1
    fi
}

# Iniciar servidor principal
start_main_server &
MAIN_PID=$!

# Esperar un momento para que el servidor inicie
sleep 5

# Verificar que todo esté funcionando
if health_check; then
    echo "🎉 Sistema Sumiller desplegado exitosamente en Railway!"
    echo "🌐 Accesible en: https://tu-dominio.railway.app"
    echo "📖 Documentación: https://tu-dominio.railway.app/docs"
else
    echo "❌ Error al iniciar el sistema"
    exit 1
fi

# Mantener el script corriendo
wait $MAIN_PID 