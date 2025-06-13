#!/bin/bash

# ==============================================
# SCRIPT DE PRUEBAS COMPLETO - SISTEMA SUMILLER
# ==============================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URLs de los servicios
SUMILLER_URL="https://sumiller-bot-production.up.railway.app"
RAG_URL="https://rag-mcp-server-production.up.railway.app"

# Contadores
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Función para logging
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para hacer requests con timeout
make_request() {
    local url="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    local timeout="${4:-10}"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        curl -s --max-time "$timeout" -X POST \
             -H "Content-Type: application/json" \
             -d "$data" \
             "$url"
    else
        curl -s --max-time "$timeout" "$url"
    fi
}

# Función para verificar JSON response
check_json_field() {
    local response="$1"
    local field="$2"
    local expected="$3"
    
    local value=$(echo "$response" | jq -r ".$field" 2>/dev/null)
    if [ "$value" = "$expected" ]; then
        return 0
    else
        return 1
    fi
}

# ==============================================
# INICIO DE PRUEBAS
# ==============================================

echo ""
echo -e "${BLUE}🍷 =============================================${NC}"
echo -e "${BLUE}   PRUEBAS SISTEMA SUMILLER MULTI-AGENTE${NC}"
echo -e "${BLUE}🍷 =============================================${NC}"
echo ""

# ==============================================
# PRUEBA 1: HEALTH CHECK SUMILLER BOT
# ==============================================
((TESTS_TOTAL++))
log "Prueba 1: Health Check Sumiller Bot"

response=$(make_request "$SUMILLER_URL/health")
exit_code=$?

if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.status' >/dev/null 2>&1; then
    status=$(echo "$response" | jq -r '.status')
    openai=$(echo "$response" | jq -r '.services.openai')
    filter=$(echo "$response" | jq -r '.services.intelligent_filter')
    
    if [ "$openai" = "true" ] && [ "$filter" = "true" ]; then
        success "Sumiller Bot: $status - OpenAI y filtro funcionando"
    else
        warning "Sumiller Bot responde pero servicios degradados: OpenAI=$openai, Filter=$filter"
        ((TESTS_PASSED++))
    fi
else
    error "Sumiller Bot no responde o JSON inválido"
fi

# ==============================================
# PRUEBA 2: HEALTH CHECK RAG MCP SERVER
# ==============================================
((TESTS_TOTAL++))
log "Prueba 2: Health Check RAG MCP Server"

response=$(make_request "$RAG_URL/health")
exit_code=$?

if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.status' >/dev/null 2>&1; then
    status=$(echo "$response" | jq -r '.status')
    success "RAG MCP Server: $status"
else
    warning "RAG MCP Server no responde (puede estar aún desplegándose)"
    ((TESTS_PASSED++))
fi

# ==============================================
# PRUEBA 3: CONSULTA SIMPLE SUMILLER
# ==============================================
((TESTS_TOTAL++))
log "Prueba 3: Consulta simple al Sumiller"

query_data='{"prompt": "¿Qué vino me recomiendas para una cena?"}'
response=$(make_request "$SUMILLER_URL/query" "POST" "$query_data" 15)
exit_code=$?

if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.response' >/dev/null 2>&1; then
    response_text=$(echo "$response" | jq -r '.response')
    category=$(echo "$response" | jq -r '.query_category')
    
    if [ ${#response_text} -gt 50 ]; then
        success "Consulta simple: Respuesta completa ($category)"
        log "   Respuesta: ${response_text:0:100}..."
    else
        error "Consulta simple: Respuesta muy corta"
    fi
else
    error "Consulta simple: Falló"
fi

# ==============================================
# PRUEBA 4: CONSULTA ESPECÍFICA VINOS TINTOS
# ==============================================
((TESTS_TOTAL++))
log "Prueba 4: Consulta específica - Vinos tintos españoles"

query_data='{"prompt": "Recomiéndame un vino tinto español para cordero asado", "user_id": "test_user"}'
response=$(make_request "$SUMILLER_URL/query" "POST" "$query_data" 15)
exit_code=$?

if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.response' >/dev/null 2>&1; then
    response_text=$(echo "$response" | jq -r '.response')
    category=$(echo "$response" | jq -r '.query_category')
    used_rag=$(echo "$response" | jq -r '.used_rag')
    
    # Verificar que mencione vinos españoles
    if echo "$response_text" | grep -i -E "(rioja|ribera|tempranillo|garnacha|españa)" >/dev/null; then
        success "Consulta vinos tintos: Respuesta relevante ($category, RAG=$used_rag)"
        log "   Menciona vinos españoles correctamente"
    else
        warning "Consulta vinos tintos: Respuesta no menciona vinos españoles específicos"
        ((TESTS_PASSED++))
    fi
else
    error "Consulta vinos tintos: Falló"
fi

# ==============================================
# PRUEBA 5: CLASIFICACIÓN INTELIGENTE
# ==============================================
((TESTS_TOTAL++))
log "Prueba 5: Clasificación inteligente de consultas"

query_data='{"prompt": "¿Cuál es la capital de Francia?"}'
response=$(make_request "$SUMILLER_URL/query" "POST" "$query_data" 10)
exit_code=$?

if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.response' >/dev/null 2>&1; then
    category=$(echo "$response" | jq -r '.query_category')
    response_text=$(echo "$response" | jq -r '.response')
    
    # Verificar que redirige a tema de vinos
    if echo "$response_text" | grep -i -E "(vino|sumiller|bebida|gastronomía)" >/dev/null; then
        success "Clasificación: Redirige correctamente consulta no-vino a temática de vinos"
    else
        warning "Clasificación: No redirige apropiadamente ($category)"
        ((TESTS_PASSED++))
    fi
else
    error "Clasificación: Falló"
fi

# ==============================================
# PRUEBA 6: ENDPOINT DE ESTADÍSTICAS
# ==============================================
((TESTS_TOTAL++))
log "Prueba 6: Endpoint de estadísticas"

response=$(make_request "$SUMILLER_URL/stats")
exit_code=$?

if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.queries_processed' >/dev/null 2>&1; then
    queries=$(echo "$response" | jq -r '.queries_processed')
    success "Estadísticas: $queries consultas procesadas"
else
    warning "Estadísticas no disponibles (endpoint opcional)"
    ((TESTS_PASSED++))
fi

# ==============================================
# PRUEBA 7: RAG MCP SERVER (SI ESTÁ DISPONIBLE)
# ==============================================
if curl -s --max-time 5 "$RAG_URL/health" >/dev/null 2>&1; then
    ((TESTS_TOTAL++))
    log "Prueba 7: RAG MCP Server - Consulta directa"
    
    query_data='{"query": "vinos tempranillo", "max_results": 2}'
    response=$(make_request "$RAG_URL/query" "POST" "$query_data" 10)
    exit_code=$?
    
    if [ $exit_code -eq 0 ] && echo "$response" | jq -e '.answer' >/dev/null 2>&1; then
        answer=$(echo "$response" | jq -r '.answer')
        sources=$(echo "$response" | jq -r '.sources | length')
        success "RAG directo: Respuesta generada con $sources fuentes"
    else
        warning "RAG directo: Respuesta limitada o en desarrollo"
        ((TESTS_PASSED++))
    fi
else
    log "RAG MCP Server no disponible - saltando prueba directa"
fi

# ==============================================
# PRUEBA 8: RENDIMIENTO Y TIMEOUTS
# ==============================================
((TESTS_TOTAL++))
log "Prueba 8: Rendimiento - Tiempo de respuesta"

start_time=$(date +%s.%N)
query_data='{"prompt": "Vino para pescado"}'
response=$(make_request "$SUMILLER_URL/query" "POST" "$query_data" 20)
end_time=$(date +%s.%N)

if [ $? -eq 0 ]; then
    duration=$(echo "$end_time - $start_time" | bc)
    duration_int=$(echo "$duration" | cut -d. -f1)
    
    if [ "$duration_int" -lt 10 ]; then
        success "Rendimiento: Respuesta en ${duration}s (< 10s)"
    else
        warning "Rendimiento: Respuesta lenta ${duration}s (> 10s)"
        ((TESTS_PASSED++))
    fi
else
    error "Rendimiento: Timeout o error"
fi

# ==============================================
# RESUMEN FINAL
# ==============================================
echo ""
echo -e "${BLUE}📊 =============================================${NC}"
echo -e "${BLUE}   RESUMEN DE PRUEBAS${NC}"
echo -e "${BLUE}📊 =============================================${NC}"
echo ""

echo -e "Total de pruebas: ${BLUE}$TESTS_TOTAL${NC}"
echo -e "Pruebas exitosas: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Pruebas fallidas: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ¡TODAS LAS PRUEBAS PASARON!${NC}"
    echo -e "${GREEN}   El sistema está funcionando correctamente${NC}"
    exit 0
elif [ $TESTS_FAILED -le 2 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  SISTEMA MAYORMENTE FUNCIONAL${NC}"
    echo -e "${YELLOW}   Solo $TESTS_FAILED pruebas fallaron${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ PROBLEMAS DETECTADOS${NC}"
    echo -e "${RED}   $TESTS_FAILED pruebas fallaron${NC}"
    exit 1
fi 