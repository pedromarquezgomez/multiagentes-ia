#!/bin/bash

# Script de despliegue mejorado para Cloud Run con configuración multi-entorno
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
PROJECT_ID="multiagentes-vinos"
REGION="europe-west1"
OPENAI_SECRET_NAME="openai-api-key"

echo -e "${GREEN}🚀 Iniciando despliegue en Google Cloud Run...${NC}"

# Verificar que estamos autenticados
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ No estás autenticado en gcloud. Ejecuta 'gcloud auth login'${NC}"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}🔧 Habilitando APIs necesarias...${NC}"
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com

echo -e "${YELLOW}🔍 Verificando el secreto de OpenAI...${NC}"
if ! gcloud secrets describe $OPENAI_SECRET_NAME --quiet 2>/dev/null; then
    echo -e "${RED}❌ El secreto '$OPENAI_SECRET_NAME' no existe.${NC}"
    echo "Créalo primero con:"
    echo "  echo -n 'tu-api-key' | gcloud secrets create $OPENAI_SECRET_NAME --data-file=-"
    exit 1
fi

echo -e "${YELLOW}📦 Desplegando MCP Server...${NC}"
gcloud run deploy mcp-server \
    --source ./mcp-server \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --platform managed \
    --set-env-vars ENVIRONMENT=cloud,GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --quiet

MCP_SERVER_URL=$(gcloud run services describe mcp-server --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ MCP Server desplegado en: $MCP_SERVER_URL${NC}"

echo -e "${YELLOW}🍷 Desplegando Sumiller Bot...${NC}"
gcloud run deploy sumiller-bot \
    --source ./sumiller-bot \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --platform managed \
    --set-env-vars ENVIRONMENT=cloud,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,CLOUD_MCP_SERVER_URL=$MCP_SERVER_URL \
    --set-secrets OPENAI_API_KEY=$OPENAI_SECRET_NAME:latest \
    --quiet

SUMILLER_URL=$(gcloud run services describe sumiller-bot --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Sumiller Bot desplegado en: $SUMILLER_URL${NC}"

echo -e "${YELLOW}🎩 Desplegando Maitre Bot...${NC}"
gcloud run deploy maitre-bot \
    --source ./maitre-bot \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --platform managed \
    --set-env-vars ENVIRONMENT=cloud,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,CLOUD_SUMILLER_URL=$SUMILLER_URL \
    --quiet

MAITRE_URL=$(gcloud run services describe maitre-bot --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Maitre Bot desplegado en: $MAITRE_URL${NC}"

echo -e "${YELLOW}🌐 Desplegando UI...${NC}"
# Construir la UI con la URL del maitre
cd ui
VITE_MAITRE_URL=$MAITRE_URL npm run build

# Desplegar en Firebase Hosting
firebase deploy --only hosting
cd ..

echo ""
echo -e "${GREEN}🎉 ¡Despliegue completado exitosamente!${NC}"
echo ""
echo -e "${GREEN}📊 URLs de los servicios:${NC}"
echo -e "  🎩 Maitre Bot: $MAITRE_URL"
echo -e "  🍷 Sumiller Bot: $SUMILLER_URL"
echo -e "  📚 MCP Server: $MCP_SERVER_URL"
echo ""
echo -e "${YELLOW}💾 Variables de entorno para .env:${NC}"
echo "CLOUD_MAITRE_URL=$MAITRE_URL"
echo "CLOUD_SUMILLER_URL=$SUMILLER_URL"
echo "CLOUD_MCP_SERVER_URL=$MCP_SERVER_URL"
echo ""
echo -e "${GREEN}🔗 Tu aplicación estará disponible en:${NC}"
echo "  https://tu-proyecto.web.app"
echo "" 