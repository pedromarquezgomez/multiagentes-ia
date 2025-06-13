#!/bin/bash

# 🚂 PASO 1: Deployment Sumiller Bot en Railway
# ============================================

echo "🚀 PASO 1: Preparando deployment del Sumiller Bot..."
echo ""

# Verificar que estamos en el directorio correcto
if [[ ! -f "sumiller-bot/main.py" ]]; then
    echo "❌ Error: Ejecuta este script desde multiagent-restaurant/"
    exit 1
fi

echo "📋 INFORMACIÓN PARA RAILWAY DASHBOARD:"
echo "======================================"
echo ""
echo "🔧 CONFIGURACIÓN DEL SERVICIO:"
echo "  - Service Name: sumiller-bot"
echo "  - Source: GitHub Repository"
echo "  - Root Directory: multiagent-restaurant"
echo "  - Dockerfile Path: sumiller-bot/Dockerfile.railway"
echo ""

echo "🔐 VARIABLES DE ENTORNO (copiar en Railway):"
echo "============================================"
echo "ENVIRONMENT=railway"
echo "OPENAI_API_KEY=sk-proj-TU_OPENAI_API_KEY_AQUI"
echo "OPENAI_BASE_URL=https://api.openai.com/v1"
echo "OPENAI_MODEL=gpt-4o-mini"
echo ""

echo "⚠️  IMPORTANTE - API KEY:"
echo "========================="
echo "❗ Reemplaza 'sk-proj-TU_OPENAI_API_KEY_AQUI' con tu API key real de OpenAI"
echo "🔗 Obtén tu API key en: https://platform.openai.com/api-keys"
echo "⚡ Tu API key actual empieza por: sk-proj-UTuupku2..."
echo ""

echo "📝 PASOS A SEGUIR:"
echo "=================="
echo "1. Ve a Railway Dashboard: https://railway.app/"
echo "2. Click 'New Service' → 'GitHub Repo'"
echo "3. Selecciona tu repositorio multiagentes-ia"
echo "4. Configura:"
echo "   - Service Name: sumiller-bot"
echo "   - Root Directory: multiagent-restaurant"
echo "   - Dockerfile Path: sumiller-bot/Dockerfile.railway"
echo "5. En Variables, añade las 4 variables de arriba (¡con tu API key real!)"
echo "6. Click 'Deploy'"
echo ""

echo "✅ VERIFICACIÓN (después del deploy):"
echo "====================================="
echo "1. Espera a que termine el deployment"
echo "2. Anota la URL generada (algo como sumiller-bot-xxxxx.railway.app)"
echo "3. Prueba: https://TU-URL/health"
echo "4. Debería responder con status: 'operational'"
echo ""

echo "🔄 SIGUIENTE PASO:"
echo "=================="
echo "Cuando el Paso 1 esté funcionando, ejecuta:"
echo "  ./step2-redis-database.sh"
echo ""

echo "💡 AYUDA:"
echo "========"
echo "Si tienes problemas, verifica:"
echo "- El Dockerfile existe en sumiller-bot/Dockerfile.railway"
echo "- Las variables están copiadas exactamente"
echo "- El repositorio está conectado a Railway"
echo "- Tu API key de OpenAI es válida"
echo ""

echo "🚀 ¡Listo para empezar! Ve a Railway Dashboard." 