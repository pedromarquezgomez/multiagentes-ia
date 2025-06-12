#!/bin/bash

# ===============================================
# Script de Verificación - MCP Agentic RAG Local
# ===============================================

echo "🔍 Verificando configuración para despliegue local..."
echo "================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success=0
warnings=0
errors=0

check_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((success++))
}

check_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((warnings++))
}

check_error() {
    echo -e "${RED}❌ $1${NC}"
    ((errors++))
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo ""
echo "📋 Verificando prerrequisitos..."

# Verificar Docker
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        check_success "Docker está instalado y corriendo"
    else
        check_error "Docker está instalado pero no está corriendo"
        echo "   💡 Solución: Iniciar Docker Desktop"
    fi
else
    check_error "Docker no está instalado"
    echo "   💡 Solución: Instalar Docker Desktop"
fi

# Verificar Docker Compose
if docker compose version &> /dev/null; then
    check_success "Docker Compose está disponible"
else
    check_error "Docker Compose no está disponible"
fi

echo ""
echo "⚙️  Verificando configuración..."

# Verificar archivo .env
if [ -f .env ]; then
    check_success "Archivo .env encontrado"
    
    # Verificar OPENAI_API_KEY
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "your-openai-api-key" .env; then
        check_success "OPENAI_API_KEY configurada en .env"
    else
        check_error "OPENAI_API_KEY no configurada correctamente en .env"
        echo "   💡 Solución: Editar .env y agregar OPENAI_API_KEY=sk-tu-clave-aqui"
    fi
else
    # Verificar variable de entorno
    if [ -n "$OPENAI_API_KEY" ] && [[ "$OPENAI_API_KEY" != *"your-openai-api-key"* ]]; then
        check_success "OPENAI_API_KEY configurada como variable de entorno"
    else
        check_error "Archivo .env no encontrado y OPENAI_API_KEY no configurada"
        echo "   💡 Solución 1: Crear archivo .env basado en .env.example"
        echo "   💡 Solución 2: export OPENAI_API_KEY=sk-tu-clave-aqui"
    fi
fi

# Verificar puertos
echo ""
echo "🔌 Verificando puertos disponibles..."

check_port() {
    local port=$1
    local service=$2
    if lsof -i :$port &> /dev/null; then
        check_warning "Puerto $port ($service) está ocupado"
        echo "   💡 Solución: Liberar puerto o parar otros servicios"
        return 1
    else
        check_success "Puerto $port ($service) disponible"
        return 0
    fi
}

check_port 8000 "RAG MCP Server"
check_port 8001 "Sumiller Bot"
check_port 8002 "Memory MCP Server"
check_port 3000 "UI Frontend"
check_port 6379 "Redis"
check_port 8004 "ChromaDB"

echo ""
echo "📁 Verificando estructura de archivos..."

# Verificar archivos clave
files=(
    "docker-compose.yaml:Configuración principal de Docker"
    "start-local.sh:Script de inicio"
    "tester.sh:Suite de testing"
    "config.py:Configuración multi-entorno"
    "mcp-agentic-rag/rag_mcp_server.py:Servidor RAG MCP"
    "mcp-agentic-rag/memory_mcp_server.py:Servidor Memory MCP"
    "sumiller-bot/main.py:Sumiller Bot actualizado"
    "ui/package.json:Frontend UI"
)

for file_desc in "${files[@]}"; do
    file=$(echo $file_desc | cut -d: -f1)
    desc=$(echo $file_desc | cut -d: -f2)
    if [ -f "$file" ]; then
        check_success "$desc encontrado"
    else
        check_error "$desc no encontrado ($file)"
    fi
done

# Verificar Dockerfiles
echo ""
echo "🐳 Verificando Dockerfiles..."

dockerfiles=(
    "mcp-agentic-rag/docker/Dockerfile.rag-server:Dockerfile RAG Server"
    "mcp-agentic-rag/docker/Dockerfile.memory-server:Dockerfile Memory Server"
    "sumiller-bot/Dockerfile:Dockerfile Sumiller Bot"
    "ui/Dockerfile:Dockerfile UI"
)

for dockerfile_desc in "${dockerfiles[@]}"; do
    dockerfile=$(echo $dockerfile_desc | cut -d: -f1)
    desc=$(echo $dockerfile_desc | cut -d: -f2)
    if [ -f "$dockerfile" ]; then
        check_success "$desc encontrado"
    else
        check_error "$desc no encontrado ($dockerfile)"
    fi
done

echo ""
echo "🧪 Verificando scripts de testing..."

if [ -x "tester.sh" ]; then
    check_success "Script tester.sh es ejecutable"
else
    check_warning "Script tester.sh no es ejecutable"
    echo "   💡 Solución: chmod +x tester.sh"
fi

if [ -x "start-local.sh" ]; then
    check_success "Script start-local.sh es ejecutable"
else
    check_warning "Script start-local.sh no es ejecutable"
    echo "   💡 Solución: chmod +x start-local.sh"
fi

echo ""
echo "📊 Resumen de verificación:"
echo "================================"
echo -e "${GREEN}✅ Éxitos: $success${NC}"
if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Advertencias: $warnings${NC}"
fi
if [ $errors -gt 0 ]; then
    echo -e "${RED}❌ Errores: $errors${NC}"
fi

echo ""
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡Sistema listo para despliegue local!${NC}"
    echo ""
    echo "🚀 Para iniciar el sistema:"
    echo "   ./start-local.sh"
    echo ""
    echo "🧪 Para probar el sistema:"
    echo "   ./tester.sh health"
    echo "   ./tester.sh full"
    echo ""
    echo "📱 Acceder a la UI: http://localhost:3000"
else
    echo -e "${RED}🚫 Se encontraron errores que deben resolverse antes del despliegue${NC}"
    echo ""
    echo "💡 Revisa los errores arriba y ejecuta nuevamente este script"
fi 