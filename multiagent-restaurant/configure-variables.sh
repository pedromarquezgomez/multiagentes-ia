#!/bin/bash
# 🔧 Configurar Variables de Entorno en Railway

echo "🔧 Configurando variables de entorno para el Sumiller Bot..."

# Verificar que estamos conectados
if ! railway status &> /dev/null; then
    echo "❌ Error: Proyecto no está linkeado"
    echo "   Ejecuta: railway link"
    exit 1
fi

echo "📝 Variables requeridas para el funcionamiento completo:"
echo "   - OPENAI_API_KEY (REQUERIDA)"
echo "   - OPENAI_BASE_URL"
echo "   - OPENAI_MODEL"
echo "   - ENVIRONMENT"
echo ""

# Solicitar API Key si no se proporciona
if [ -z "$OPENAI_API_KEY" ]; then
    echo "🔑 Ingresa tu OpenAI API Key:"
    echo "   (Debe empezar con 'sk-' y tener ~51 caracteres)"
    read -p "   API Key: " openai_key
    
    if [ -z "$openai_key" ]; then
        echo "❌ API Key es requerida"
        exit 1
    fi
    
    if [[ ! $openai_key =~ ^sk- ]]; then
        echo "❌ API Key debe empezar con 'sk-'"
        exit 1
    fi
    
    OPENAI_API_KEY="$openai_key"
fi

echo ""
echo "🚀 Configurando variables en Railway..."

# Configurar variables principales
railway variables --set "ENVIRONMENT=railway"
railway variables --set "OPENAI_API_KEY=$OPENAI_API_KEY"
railway variables --set "OPENAI_BASE_URL=https://api.openai.com/v1"
railway variables --set "OPENAI_MODEL=gpt-4o-mini"

# Variables adicionales para optimización
railway variables --set "HTTP_POOL_MAX_CONNECTIONS=100"
railway variables --set "CIRCUIT_BREAKER_FAILURE_THRESHOLD=3"

echo ""
echo "✅ Variables configuradas!"

echo ""
echo "📋 Variables actuales:"
railway variables

echo ""
echo "🔄 Para aplicar los cambios, redespliega el servicio:"
echo "   railway up --detach"

echo ""
echo "🧪 Después del redeploy, verifica con:"
echo "   ./verify-deployment.sh" 