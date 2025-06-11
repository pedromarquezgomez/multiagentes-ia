#!/bin/bash

# Script de desarrollo local para Sumy Wine Recommender
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🍷 Iniciando entorno de desarrollo local - Sumy Wine Recommender${NC}"

# Verificar que Docker Compose está disponible
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado o no está en el PATH.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está disponible.${NC}"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️ No se encontró archivo .env, copiando desde .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Por favor, edita el archivo .env con tu OpenAI API Key${NC}"
        echo -e "${YELLOW}   OPENAI_API_KEY=sk-proj-tu-key-aqui${NC}"
        read -p "Presiona Enter cuando hayas configurado la API key..."
    else
        echo -e "${RED}❌ No existe .env.example. Creando .env básico...${NC}"
        cat > .env << EOF
ENVIRONMENT=local
OPENAI_API_KEY=sk-proj-your-key-here
MAITRE_PORT=8000
SUMILLER_PORT=8001
MCP_SERVER_PORT=8002
UI_PORT=3000
EOF
        echo -e "${YELLOW}📝 Edita el archivo .env con tu OpenAI API Key${NC}"
        exit 1
    fi
fi

# Verificar que la API key está configurada
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-proj-your-key-here" ]; then
    echo -e "${RED}❌ OpenAI API Key no configurada en .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API Key configurada${NC}"

# Función para cleanup
cleanup() {
    echo -e "\n${YELLOW}🧹 Limpiando contenedores...${NC}"
    docker compose down
    exit 0
}

# Capturar Ctrl+C para cleanup
trap cleanup SIGINT

echo -e "${YELLOW}🔧 Construyendo imágenes...${NC}"
docker compose build

echo -e "${YELLOW}🚀 Iniciando servicios...${NC}"
docker compose up -d

echo -e "${GREEN}✅ Servicios iniciados${NC}"
echo ""
echo -e "${GREEN}📊 URLs disponibles:${NC}"
echo -e "  🎩 Maitre Bot (API): http://localhost:8000"
echo -e "  🍷 Sumiller Bot (API): http://localhost:8001"
echo -e "  📚 MCP Server (API): http://localhost:8002"
echo -e "  🌐 UI (Frontend): http://localhost:3000"
echo ""
echo -e "${GREEN}🔍 Health checks:${NC}"
echo -e "  curl http://localhost:8000/health"
echo -e "  curl http://localhost:8001/health"
echo -e "  curl http://localhost:8002/health"
echo ""
echo -e "${YELLOW}📋 Para ver logs:${NC}"
echo -e "  docker compose logs -f [servicio]"
echo ""
echo -e "${YELLOW}🛑 Para detener:${NC}"
echo -e "  docker compose down"
echo ""

# Mostrar logs en tiempo real
echo -e "${GREEN}📜 Mostrando logs (Ctrl+C para detener):${NC}"
docker compose logs -f 