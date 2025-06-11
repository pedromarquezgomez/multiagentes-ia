#!/bin/bash

# ===============================================
# Script de Inicio para MCP Agentic RAG (Local)
# ===============================================

set -e  # Salir en caso de error

echo "🍷 Iniciando Sistema MCP Agentic RAG - Sumy Wine Recommender"
echo "=================================================="

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Verificar que Docker Compose esté disponible
if ! docker compose version > /dev/null 2>&1; then
    echo "❌ Error: Docker Compose no está disponible."
    exit 1
fi

# Verificar archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Usando configuración por defecto."
    echo "📝 Para configurar variables personalizadas, crea un archivo .env basado en:"
    echo "   - OPENAI_API_KEY=sk-your-api-key"
    echo "   - ENVIRONMENT=local"
    echo ""
    
    # Verificar OPENAI_API_KEY
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ Error: OPENAI_API_KEY no está configurada."
        echo "💡 Configúrala con: export OPENAI_API_KEY=sk-your-api-key"
        echo "💡 O crea un archivo .env con: OPENAI_API_KEY=sk-your-api-key"
        exit 1
    fi
fi

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Puerto $port está en uso. El servicio puede fallar al iniciar."
        return 1
    fi
    return 0
}

# Verificar puertos principales
echo "🔍 Verificando puertos disponibles..."
check_port 8000 || echo "   - Puerto 8000 (RAG MCP Server) ocupado"
check_port 8001 || echo "   - Puerto 8001 (Sumiller Bot) ocupado"
check_port 8002 || echo "   - Puerto 8002 (Memory MCP Server) ocupado"
check_port 3000 || echo "   - Puerto 3000 (UI) ocupado"
check_port 6379 || echo "   - Puerto 6379 (Redis) ocupado"

echo ""
echo "🚀 Construyendo e iniciando servicios..."

# Limpiar contenedores anteriores si existen
echo "🧹 Limpiando contenedores anteriores..."
docker compose down --remove-orphans 2>/dev/null || true

# Construir e iniciar servicios
echo "🔨 Construyendo imágenes Docker..."
docker compose build --no-cache

echo "⚡ Iniciando servicios en modo detached..."
docker compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."

wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "   - Esperando $service_name"
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo " ✅"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo " ❌ (timeout)"
    return 1
}

# Verificar servicios uno por uno
wait_for_service "RAG MCP Server" "http://localhost:8000/health"
wait_for_service "Memory MCP Server" "http://localhost:8002/health"  
wait_for_service "Sumiller Bot" "http://localhost:8001/health"

echo ""
echo "🎉 ¡Sistema iniciado correctamente!"
echo ""
echo "📋 Servicios disponibles:"
echo "   🤖 Sumiller Bot:        http://localhost:8001"
echo "   🧠 RAG MCP Server:      http://localhost:8000"
echo "   💾 Memory MCP Server:   http://localhost:8002"
echo "   🌐 UI Frontend:         http://localhost:3000"
echo "   🧪 MCP Tester:          http://localhost:8003"
echo "   📊 ChromaDB:            http://localhost:8004"
echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs:               docker compose logs -f"
echo "   Ver logs específicos:   docker compose logs -f sumiller-bot"
echo "   Parar servicios:        docker compose down"
echo "   Reiniciar:              docker compose restart"
echo ""
echo "🧪 Para probar el sistema:"
echo "   bash tester.sh health    # Verificar estado de servicios"
echo "   bash tester.sh full      # Prueba completa del sistema"
echo ""
echo "📱 Accede a la UI en: http://localhost:3000" 