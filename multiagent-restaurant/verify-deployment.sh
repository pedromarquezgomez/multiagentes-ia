#!/bin/bash
# 🔍 Script de Verificación Completa del Despliegue
# Verifica que todos los servicios estén funcionando correctamente

set -e

echo "🔍 Verificando despliegue del Sistema Sumiller..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Función para mostrar info
show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Función para mostrar warning
show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
echo "1️⃣  VERIFICANDO RAILWAY CLI Y CONEXIÓN"
echo "------------------------------------"

# Verificar Railway CLI
if command -v railway &> /dev/null; then
    show_status 0 "Railway CLI instalado"
    railway --version
else
    show_status 1 "Railway CLI no está instalado"
    echo "   Ejecuta: ./setup-railway.sh"
    exit 1
fi

# Verificar conexión
if railway whoami &> /dev/null; then
    show_status 0 "Conectado a Railway"
    show_info "Usuario: $(railway whoami)"
else
    show_status 1 "No conectado a Railway"
    echo "   Ejecuta: railway login"
    exit 1
fi

# Verificar proyecto linkeado
if railway status &> /dev/null; then
    show_status 0 "Proyecto linkeado"
else
    show_status 1 "Proyecto no linkeado"
    echo "   Ejecuta: railway link"
    exit 1
fi

echo ""
echo "2️⃣  VERIFICANDO ESTADO DEL SERVICIO"
echo "-----------------------------------"

# Estado del servicio
echo "📊 Estado del servicio:"
railway status

# Verificar si está desplegado
if railway status | grep -q "Deployed"; then
    show_status 0 "Servicio desplegado"
elif railway status | grep -q "Building"; then
    show_warning "Servicio en construcción"
    echo "   Espera a que termine el build..."
elif railway status | grep -q "Failed"; then
    show_status 1 "Despliegue falló"
    echo "   Revisa logs: railway logs"
    echo "   Redespliega: railway up"
else
    show_warning "Estado desconocido"
fi

echo ""
echo "3️⃣  OBTENIENDO URL DEL SERVICIO"
echo "-------------------------------"

# Obtener URL del servicio
SERVICE_URL=$(railway status 2>/dev/null | grep -o 'https://[^[:space:]]*' || echo "")

if [ ! -z "$SERVICE_URL" ]; then
    show_status 0 "URL obtenida"
    show_info "URL del servicio: $SERVICE_URL"
    
    echo ""
    echo "4️⃣  VERIFICANDO HEALTH CHECK"
    echo "----------------------------"
    
    # Test health check
    echo "🔍 Probando health check..."
    if curl -f -s "${SERVICE_URL}/health" > /dev/null; then
        show_status 0 "Health check OK"
        echo "   Respuesta:"
        curl -s "${SERVICE_URL}/health" | jq . 2>/dev/null || curl -s "${SERVICE_URL}/health"
    else
        show_status 1 "Health check falló"
        echo "   URL probada: ${SERVICE_URL}/health"
    fi
    
    echo ""
    echo "5️⃣  VERIFICANDO API PRINCIPAL"
    echo "-----------------------------"
    
    # Test API principal
    echo "🔍 Probando endpoint principal..."
    TEST_PAYLOAD='{"prompt": "Hola, ¿funciona el sistema?", "user_id": "test_verification"}'
    
    echo "   Enviando: $TEST_PAYLOAD"
    echo "   A: ${SERVICE_URL}/query"
    
    if curl -f -s -X POST "${SERVICE_URL}/query" \
        -H "Content-Type: application/json" \
        -d "$TEST_PAYLOAD" > /tmp/api_response.json; then
        
        show_status 0 "API principal OK"
        echo "   Respuesta:"
        cat /tmp/api_response.json | jq . 2>/dev/null || cat /tmp/api_response.json
        rm -f /tmp/api_response.json
    else
        show_status 1 "API principal falló"
        show_info "Posibles causas:"
        echo "     - Variables de entorno no configuradas"
        echo "     - OpenAI API key inválida"
        echo "     - Servicios MCP no conectados"
    fi
    
else
    show_status 1 "No se pudo obtener URL del servicio"
    echo "   El servicio puede no estar desplegado correctamente"
fi

echo ""
echo "6️⃣  VERIFICANDO VARIABLES DE ENTORNO"
echo "------------------------------------"

echo "🔍 Variables de entorno configuradas:"
railway variables | grep -E "(ENVIRONMENT|OPENAI|PORT)" || echo "   No se encontraron variables principales"

echo ""
echo "7️⃣  VERIFICANDO LOGS RECIENTES"
echo "------------------------------"

echo "📝 Últimos logs:"
railway logs | tail -10

echo ""
echo "=================================================="
echo "🎯 RESUMEN DE VERIFICACIÓN"
echo "=================================================="

if [ ! -z "$SERVICE_URL" ]; then
    echo "🔗 URL del servicio: $SERVICE_URL"
    echo ""
    echo "🧪 Comandos de test manual:"
    echo "   Health check: curl $SERVICE_URL/health"
    echo "   Test API:     curl -X POST $SERVICE_URL/query \\"
    echo "                   -H 'Content-Type: application/json' \\"
    echo "                   -d '{\"prompt\": \"Hola\", \"user_id\": \"test\"}'"
    echo ""
    echo "📊 Monitoreo continuo:"
    echo "   Ver logs:     railway logs --tail"
    echo "   Ver estado:   railway status"
    echo "   Ver métricas: railway metrics"
fi

echo ""
echo "🔧 Si hay problemas:"
echo "   1. Verificar variables de entorno: railway variables"
echo "   2. Ver logs completos: railway logs"
echo "   3. Redesplegar: railway up"
echo "   4. Ver guía: cat railway-setup.md"

echo ""
echo "✨ Verificación completada!" 