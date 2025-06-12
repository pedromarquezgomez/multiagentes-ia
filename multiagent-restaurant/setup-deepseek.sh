#!/bin/bash

# ===========================================
# CONFIGURADOR DEEPSEEK PARA SISTEMA SUMILLER
# ===========================================

echo "🤖 Configurador DeepSeek para Sistema Sumiller"
echo "=============================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar si existe archivo .env
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env ya existe. Haciendo backup...${NC}"
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Backup creado${NC}"
fi

# Crear archivo .env desde example
echo -e "${BLUE}📄 Creando archivo .env...${NC}"
cp env.example .env

echo ""
echo -e "${YELLOW}🔑 CONFIGURACIÓN DEEPSEEK REQUERIDA:${NC}"
echo ""
echo "1. Obtén tu API key de DeepSeek:"
echo "   👉 https://platform.deepseek.com/"
echo ""
echo "2. Edita el archivo .env y cambia:"
echo "   DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here"
echo "   por tu API key real"
echo ""
echo -e "${GREEN}📝 COMANDOS ÚTILES:${NC}"
echo ""
echo "# Editar configuración:"
echo "nano .env"
echo ""
echo "# Iniciar sistema local:"
echo "docker-compose up -d"
echo ""
echo "# Cargar datos de vinos:"
echo "python3 load-wines.py"
echo ""
echo "# Ver logs del sumiller:"
echo "docker-compose logs -f sumiller-bot"
echo ""
echo "# Probar sistema:"
echo "curl -X POST 'http://localhost:8001/query' -H 'Content-Type: application/json' -d '{\"prompt\": \"Recomienda un vino tinto\", \"user_id\": \"test\"}'"
echo ""
echo -e "${BLUE}🌐 URLS DEL SISTEMA:${NC}"
echo "Frontend: http://localhost:3000"
echo "Sumiller API: http://localhost:8001"
echo "ChromaDB: http://localhost:8000"
echo ""
echo -e "${GREEN}✅ Configuración completada. Edita .env con tu API key de DeepSeek${NC}" 