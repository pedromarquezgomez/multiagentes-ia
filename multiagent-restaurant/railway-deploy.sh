#!/bin/bash
# 🚂 Script de Deploy Automatizado para Railway
# Sistema Sumiller Multi-Agente

set -e  # Salir si hay algún error

echo "🚂 Iniciando deploy del Sistema Sumiller en Railway..."

# Verificar que estamos en el directorio correcto
if [ ! -f "railway.json" ]; then
    echo "❌ Error: No se encontró railway.json"
    echo "   Ejecuta este script desde el directorio multiagent-restaurant"
    exit 1
fi

# Verificar que Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Error: Railway CLI no está instalado"
    echo "   Instala con: npm install -g @railway/cli"
    exit 1
fi

# Verificar que estamos logueados
if ! railway whoami &> /dev/null; then
    echo "❌ Error: No estás logueado en Railway"
    echo "   Ejecuta: railway login"
    exit 1
fi

echo "✅ Prerequisitos verificados"

# Función para crear y configurar un servicio
deploy_service() {
    local service_name=$1
    local config_file=$2
    local description=$3
    
    echo ""
    echo "🚀 Desplegando $description..."
    echo "   Servicio: $service_name"
    echo "   Config: $config_file"
    
    # Verificar que el archivo de configuración existe
    if [ ! -f "$config_file" ]; then
        echo "❌ Error: No se encontró $config_file"
        return 1
    fi
    
    # Crear y desplegar el servicio
    echo "   Desplegando servicio..."
    if railway up --service "$service_name" --config "$config_file"; then
        echo "✅ $description desplegado exitosamente"
        
        # Obtener la URL del servicio
        local service_url=$(railway domain --service "$service_name" 2>/dev/null || echo "URL no disponible aún")
        echo "   URL: $service_url"
    else
        echo "❌ Error al desplegar $description"
        return 1
    fi
}

# 1. Desplegar RAG MCP Server
deploy_service "rag-mcp-server" "railway.rag.json" "RAG MCP Server"

# 2. Desplegar Memory MCP Server  
deploy_service "memory-mcp-server" "railway.memory.json" "Memory MCP Server"

# 3. Desplegar Sumiller Bot (Principal)
deploy_service "sumiller-bot" "railway.json" "Sumiller Bot Principal"

# 4. Información sobre UI Frontend
echo ""
echo "📝 Nota: El Frontend UI se despliega en Firebase separadamente"
echo "   Guía: Ver sección 'Firebase UI Deployment' en railway-setup.md"

echo ""
echo "🎉 ¡Deploy completado!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar variables de entorno en Railway Dashboard"
echo "2. Crear base de datos Redis en Railway"
echo "3. Verificar health checks de los servicios"
echo "4. Desplegar UI en Firebase (ver railway-setup.md)"
echo ""
echo "📖 Ver guía completa en: railway-setup.md"
echo ""

# Mostrar URLs de los servicios desplegados
echo "🔗 URLs de tus servicios:"
for service in "rag-mcp-server" "memory-mcp-server" "sumiller-bot"; do
    url=$(railway domain --service "$service" 2>/dev/null || echo "No desplegado")
    if [ "$url" != "No desplegado" ]; then
        echo "   $service: $url"
    fi
done
echo "   UI Frontend: Se desplegará en Firebase"

echo ""
echo "✨ ¡Sistema Sumiller desplegado en Railway!" 