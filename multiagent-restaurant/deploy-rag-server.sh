#!/bin/bash
# 🔍 Script para Desplegar RAG MCP Server en Railway

echo "🔍 Desplegando RAG MCP Server..."

# Verificar conexión
if ! railway status &> /dev/null; then
    echo "❌ Error: Proyecto no está linkeado"
    echo "   Ejecuta: railway link"
    exit 1
fi

echo "📋 Para desplegar el RAG MCP Server necesitas:"
echo "   1. Ir al dashboard de Railway"
echo "   2. Añadir nuevo servicio"
echo "   3. Seleccionar 'GitHub Repo'"
echo "   4. Configurar variables de entorno"
echo ""

echo "🌐 Abriendo Railway Dashboard..."
railway open

echo ""
echo "📝 INSTRUCCIONES PASO A PASO:"
echo "================================="
echo ""
echo "1️⃣  En el Dashboard de Railway:"
echo "   - Click en '+ New Service'"
echo "   - Selecciona 'GitHub Repo'"
echo "   - Conecta tu repositorio"
echo "   - Selecciona la rama correcta"
echo ""
echo "2️⃣  Configurar el servicio:"
echo "   - Nombre del servicio: 'rag-mcp-server'"
echo "   - Root Directory: '/multiagent-restaurant'"
echo "   - Dockerfile Path: 'mcp-agentic-rag/Dockerfile.railway-rag'"
echo ""
echo "3️⃣  Variables de entorno a configurar:"
echo "   ENVIRONMENT=railway"
echo "   OPENAI_API_KEY=sk-proj-TU_OPENAI_API_KEY_AQUI"
echo "   OPENAI_BASE_URL=https://api.openai.com/v1"
echo "   OPENAI_MODEL=gpt-4o-mini"
echo "   VECTOR_DB_TYPE=chroma"
echo ""
echo "4️⃣  Después del deploy:"
echo "   - Anota la URL del servicio"
echo "   - Actualiza el Sumiller Bot con la nueva URL"
echo ""

# Preparar las variables para copiar-pegar
echo "🔧 Variables listas para copiar-pegar:"
echo "======================================"
echo "ENVIRONMENT=railway"
echo "OPENAI_API_KEY=sk-proj-TU_OPENAI_API_KEY_AQUI"
echo "OPENAI_BASE_URL=https://api.openai.com/v1"
echo "OPENAI_MODEL=gpt-4o-mini"
echo "VECTOR_DB_TYPE=chroma"

echo ""
echo "⏳ Una vez completado el deploy, ejecuta:"
echo "   ./configure-rag-connection.sh" 