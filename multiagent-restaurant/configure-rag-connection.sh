#!/bin/bash
# 🔗 Configurar conexión entre Sumiller Bot y RAG MCP Server

echo "🔗 Configurando conexión RAG MCP Server..."

# Verificar conexión a Railway
if ! railway status &> /dev/null; then
    echo "❌ Error: Proyecto no está linkeado"
    exit 1
fi

echo "📝 Necesito la URL del RAG MCP Server que acabas de desplegar"
echo ""

# Solicitar URL del RAG MCP Server
read -p "🔍 Ingresa la URL del RAG MCP Server (ej: https://rag-mcp-server-xxxxx.railway.app): " rag_url

if [ -z "$rag_url" ]; then
    echo "❌ URL es requerida"
    exit 1
fi

# Validar que la URL sea válida
if [[ ! $rag_url =~ ^https:// ]]; then
    echo "❌ URL debe empezar con https://"
    exit 1
fi

echo ""
echo "🧪 Probando conexión al RAG MCP Server..."

# Test del RAG MCP Server
if curl -f -s "${rag_url}/health" > /dev/null; then
    echo "✅ RAG MCP Server está funcionando"
    echo "   Respuesta:"
    curl -s "${rag_url}/health" | head -c 200
    echo ""
else
    echo "❌ RAG MCP Server no responde"
    echo "   URL probada: ${rag_url}/health"
    echo "   Verifica que el servicio esté desplegado correctamente"
    exit 1
fi

echo ""
echo "🔧 Configurando Sumiller Bot para usar RAG MCP Server..."

# Configurar la URL en el Sumiller Bot
railway variables --set "RAG_MCP_URL=${rag_url}"

echo "✅ Variable configurada: RAG_MCP_URL=${rag_url}"

echo ""
echo "🔄 Redesplegando Sumiller Bot para aplicar cambios..."

# Redesplegar el Sumiller Bot
railway up --detach

echo ""
echo "⏳ Esperando que el redespliegue termine..."
sleep 20

echo ""
echo "🧪 Probando integración completa..."

# Test de integración
echo "🔍 Probando búsqueda en la base de conocimientos..."

test_query='{"prompt": "¿Qué sabes sobre vinos Tempranillo?", "user_id": "test_rag"}'
echo "   Enviando: $test_query"

if curl -f -s -X POST "https://multiagentes-ia-production.up.railway.app/query" \
    -H "Content-Type: application/json" \
    -d "$test_query" > /tmp/rag_test.json; then
    
    echo "✅ Integración RAG funcionando"
    echo "   Respuesta (primeros 300 caracteres):"
    cat /tmp/rag_test.json | head -c 300
    echo "..."
    
    # Verificar si usó RAG
    if grep -q '"used_rag":true' /tmp/rag_test.json; then
        echo ""
        echo "🎉 ¡RAG MCP Server integrado correctamente!"
        echo "   El sumiller ahora tiene acceso a la base de conocimientos"
    else
        echo ""
        echo "⚠️  Integración parcial - RAG no se está usando"
        echo "   Puede necesitar tiempo para sincronizar"
    fi
    
    rm -f /tmp/rag_test.json
else
    echo "❌ Error en la integración"
    echo "   Verifica los logs: railway logs"
fi

echo ""
echo "📊 Estado final del sistema:"
echo "=============================="
echo "✅ Sumiller Bot: https://multiagentes-ia-production.up.railway.app"
echo "✅ RAG MCP Server: ${rag_url}"
echo ""
echo "🧪 URLs de prueba:"
echo "   Health Sumiller: https://multiagentes-ia-production.up.railway.app/health"
echo "   Health RAG:      ${rag_url}/health"
echo "   Search RAG:      ${rag_url}/search?q=tempranillo"

echo ""
echo "🎯 Próximos pasos opcionales:"
echo "   1. Desplegar Memory MCP Server (memoria conversacional)"
echo "   2. Desplegar UI Frontend (interfaz web)"
echo "   3. Cargar más datos en la base de conocimientos" 