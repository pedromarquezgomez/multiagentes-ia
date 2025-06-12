#!/bin/bash

# Script de despliegue para Cloud Run con sistema MCP Agentic RAG
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
PROJECT_ID="maitre-ia"
REGION="europe-west1"
OPENAI_SECRET_NAME="openai-api-key"

echo -e "${GREEN}🚀 Iniciando despliegue del Sistema MCP Agentic RAG...${NC}"

# Verificar que estamos autenticados
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ No estás autenticado en gcloud. Ejecuta 'gcloud auth login'${NC}"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID --quiet

echo -e "${YELLOW}🔧 Habilitando APIs necesarias...${NC}"
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com --project=$PROJECT_ID

echo -e "${YELLOW}🔍 Verificando el secreto de OpenAI...${NC}"
if ! gcloud secrets describe $OPENAI_SECRET_NAME --project=$PROJECT_ID --quiet 2>/dev/null; then
    echo -e "${RED}❌ El secreto '$OPENAI_SECRET_NAME' no existe.${NC}"
    echo "Créalo primero con:"
    echo "  echo -n 'tu-api-key' | gcloud secrets create $OPENAI_SECRET_NAME --data-file=- --project=$PROJECT_ID"
    exit 1
fi

echo -e "${YELLOW}🧠 Desplegando RAG MCP Server...${NC}"
gcloud run deploy rag-mcp-server \
    --source ./mcp-agentic-rag \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --platform managed \
    --set-env-vars ENVIRONMENT=cloud,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,VECTOR_DB_TYPE=chroma \
    --set-secrets OPENAI_API_KEY=$OPENAI_SECRET_NAME:latest \
    --cpu-boost \
    --timeout=600s \
    --project=$PROJECT_ID \
    --quiet

RAG_MCP_URL=$(gcloud run services describe rag-mcp-server --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo -e "${GREEN}✅ RAG MCP Server desplegado en: $RAG_MCP_URL${NC}"

echo -e "${YELLOW}💾 Desplegando Memory MCP Server...${NC}"
gcloud run deploy memory-mcp-server \
    --source ./mcp-agentic-rag \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --platform managed \
    --set-env-vars ENVIRONMENT=cloud,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,MEMORY_TYPE=redis \
    --project=$PROJECT_ID \
    --quiet

MEMORY_MCP_URL=$(gcloud run services describe memory-mcp-server --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo -e "${GREEN}✅ Memory MCP Server desplegado en: $MEMORY_MCP_URL${NC}"

echo -e "${YELLOW}🍷 Desplegando Sumiller Bot Agéntico...${NC}"
gcloud run deploy sumiller-bot \
    --source ./sumiller-bot \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --platform managed \
    --set-env-vars ENVIRONMENT=cloud,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,CLOUD_RAG_MCP_URL=$RAG_MCP_URL,CLOUD_MEMORY_MCP_URL=$MEMORY_MCP_URL \
    --set-secrets OPENAI_API_KEY=$OPENAI_SECRET_NAME:latest \
    --project=$PROJECT_ID \
    --quiet

SUMILLER_URL=$(gcloud run services describe sumiller-bot --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo -e "${GREEN}✅ Sumiller Bot Agéntico desplegado en: $SUMILLER_URL${NC}"

echo -e "${YELLOW}🌐 Desplegando UI...${NC}"
# Construir la UI con la URL del sumiller
cd ui
VITE_API_BASE_URL=$SUMILLER_URL/query npm run build

# Desplegar en Firebase Hosting
firebase deploy --only hosting --project=$PROJECT_ID
cd ..

echo ""
echo -e "${GREEN}🎉 ¡Despliegue de Sistema MCP Agentic RAG completado!${NC}"
echo ""
echo -e "${GREEN}📊 URLs de los servicios:${NC}"
echo -e "  🧠 RAG MCP Server: $RAG_MCP_URL"
echo -e "  💾 Memory MCP Server: $MEMORY_MCP_URL"
echo -e "  🍷 Sumiller Bot Agéntico: $SUMILLER_URL"
echo ""
echo -e "${YELLOW}💾 Variables de entorno para .env:${NC}"
echo "CLOUD_RAG_MCP_URL=$RAG_MCP_URL"
echo "CLOUD_MEMORY_MCP_URL=$MEMORY_MCP_URL"
echo "CLOUD_SUMILLER_URL=$SUMILLER_URL"
echo ""
echo -e "${GREEN}🔗 Tu aplicación estará disponible en:${NC}"
echo "  https://maitre-ia.web.app"
echo ""
echo -e "${YELLOW}✨ Características del Sistema Agéntico:${NC}"
echo "  • Expansión inteligente de consultas"
echo "  • Memoria conversacional persistente"
echo "  • Búsqueda semántica avanzada"
echo "  • Personalización por usuario"
echo "  • Fallbacks robustos"
echo "" 