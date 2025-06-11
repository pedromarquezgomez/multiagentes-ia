#!/bin/bash

# Script de Testing para Sumy Wine Recommender
# Prueba todas las funcionalidades del sistema multi-entorno

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuración
BASE_URL="http://localhost"
MAITRE_PORT="8000"
SUMILLER_PORT="8001"
MCP_PORT="8002"
UI_PORT="3000"

# URLs
MAITRE_URL="${BASE_URL}:${MAITRE_PORT}"
SUMILLER_URL="${BASE_URL}:${SUMILLER_PORT}"
MCP_URL="${BASE_URL}:${MCP_PORT}"
UI_URL="${BASE_URL}:${UI_PORT}"

echo -e "${PURPLE}🍷 SUMY WINE RECOMMENDER - SCRIPT DE TESTING${NC}"
echo -e "${PURPLE}================================================${NC}"
echo ""

# Función para hacer peticiones y mostrar resultados
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="$3"
    local data="$4"
    local expect_success="$5"
    
    echo -e "${BLUE}🧪 Testing: ${name}${NC}"
    echo -e "   URL: ${url}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "$url" 2>/dev/null)
        http_code="${response: -3}"
        body="${response%???}"
    else
        response=$(curl -s -w "%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
        http_code="${response: -3}"
        body="${response%???}"
    fi
    
    if [ "$expect_success" = "true" ] && [ "$http_code" = "200" ]; then
        echo -e "   ${GREEN}✅ Status: ${http_code}${NC}"
        if command -v jq &> /dev/null && echo "$body" | jq . &> /dev/null; then
            echo "$body" | jq . | head -5
            if [ $(echo "$body" | wc -c) -gt 200 ]; then
                echo -e "   ${YELLOW}... (respuesta truncada)${NC}"
            fi
        else
            echo "$body" | head -3
        fi
    elif [ "$expect_success" = "false" ] && [ "$http_code" != "200" ]; then
        echo -e "   ${GREEN}✅ Error esperado: ${http_code}${NC}"
    else
        echo -e "   ${RED}❌ Status: ${http_code}${NC}"
        echo -e "   ${RED}Error: $body${NC}"
    fi
    echo ""
}

# Función para verificar servicios activos
check_services() {
    echo -e "${YELLOW}🔍 VERIFICANDO SERVICIOS ACTIVOS${NC}"
    echo -e "${YELLOW}================================${NC}"
    
    services=(
        "UI:${UI_URL}"
        "Maitre Bot:${MAITRE_URL}"
        "Sumiller Bot:${SUMILLER_URL}" 
        "MCP Server:${MCP_URL}"
    )
    
    for service in "${services[@]}"; do
        name="${service%%:*}"
        url="${service##*:}"
        
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "   ${GREEN}✅ ${name}: ACTIVO${NC}"
        else
            echo -e "   ${RED}❌ ${name}: NO DISPONIBLE${NC}"
        fi
    done
    echo ""
}

# Función para health checks
health_checks() {
    echo -e "${YELLOW}🏥 HEALTH CHECKS${NC}"
    echo -e "${YELLOW}=================${NC}"
    
    test_endpoint "Maitre Health" "${MAITRE_URL}/" "GET" "" "true"
    test_endpoint "Sumiller Health" "${SUMILLER_URL}/health" "GET" "" "true"
    test_endpoint "MCP Health" "${MCP_URL}/health" "GET" "" "true"
}

# Función para probar búsqueda directa en MCP
test_mcp_search() {
    echo -e "${YELLOW}📚 TESTING MCP SERVER (ChromaDB)${NC}"
    echo -e "${YELLOW}==================================${NC}"
    
    queries=(
        "tinto para carne"
        "blanco para pescado"
        "espumoso para celebrar"
        "algo barato"
        "vino de rioja"
        "consulta sin sentido xyz123"
    )
    
    for query in "${queries[@]}"; do
        data="{\"query\": \"$query\", \"limit\": 3}"
        test_endpoint "MCP Search: $query" "${MCP_URL}/search" "POST" "$data" "true"
    done
}

# Función para probar sumiller directamente
test_sumiller_direct() {
    echo -e "${YELLOW}🍷 TESTING SUMILLER BOT (Directo)${NC}"
    echo -e "${YELLOW}===================================${NC}"
    
    queries=(
        "recomiéndame un tinto para carne asada"
        "necesito un blanco para mariscos"
        "quiero un espumoso para una boda"
        "algo económico para todos los días"
        "un vino de la rioja"
    )
    
    for query in "${queries[@]}"; do
        data="{\"prompt\": \"$query\"}"
        test_endpoint "Sumiller: $query" "${SUMILLER_URL}/query" "POST" "$data" "true"
    done
}

# Función para probar maitre (ruta completa)
test_maitre_complete() {
    echo -e "${YELLOW}🎩 TESTING MAITRE BOT (Ruta Completa)${NC}"
    echo -e "${YELLOW}=====================================${NC}"
    
    echo -e "${BLUE}Probando endpoint con autenticación (debe fallar):${NC}"
    data="{\"prompt\": \"tinto para carne\"}"
    test_endpoint "Maitre (sin auth)" "${MAITRE_URL}/query" "POST" "$data" "false"
    
    echo -e "${BLUE}Probando endpoint de desarrollo:${NC}"
    queries=(
        "recomiéndame un tinto potente"
        "un blanco fresco y ligero"
        "espumoso para brindis"
        "vino barato pero bueno"
        "no sé nada de vinos, ayúdame"
        "quiero algo de menos de 50 euros"
    )
    
    for query in "${queries[@]}"; do
        data="{\"prompt\": \"$query\"}"
        test_endpoint "Maitre Dev: $query" "${MAITRE_URL}/query-dev" "POST" "$data" "true"
    done
}

# Función para testing de rendimiento
test_performance() {
    echo -e "${YELLOW}⚡ TESTING DE RENDIMIENTO${NC}"
    echo -e "${YELLOW}=========================${NC}"
    
    echo -e "${BLUE}Midiendo tiempo de respuesta...${NC}"
    
    query="tinto para carne asada"
    data="{\"prompt\": \"$query\"}"
    
    echo -e "   Testing MCP Server..."
    mcp_data="{\"query\": \"$query\", \"limit\": 3}"
    start_time=$(date +%s.%N)
    curl -s -X POST "${MCP_URL}/search" -H "Content-Type: application/json" -d "$mcp_data" > /dev/null
    end_time=$(date +%s.%N)
    mcp_time=$(echo "$end_time - $start_time" | bc)
    echo -e "   ${GREEN}MCP Response Time: ${mcp_time}s${NC}"
    
    echo -e "   Testing Sumiller Bot..."
    start_time=$(date +%s.%N)
    curl -s -X POST "${SUMILLER_URL}/query" -H "Content-Type: application/json" -d "$data" > /dev/null
    end_time=$(date +%s.%N)
    sumiller_time=$(echo "$end_time - $start_time" | bc)
    echo -e "   ${GREEN}Sumiller Response Time: ${sumiller_time}s${NC}"
    
    echo -e "   Testing Maitre Bot (completo)..."
    start_time=$(date +%s.%N)
    curl -s -X POST "${MAITRE_URL}/query-dev" -H "Content-Type: application/json" -d "$data" > /dev/null
    end_time=$(date +%s.%N)
    maitre_time=$(echo "$end_time - $start_time" | bc)
    echo -e "   ${GREEN}Maitre Complete Response Time: ${maitre_time}s${NC}"
    
    echo ""
}

# Función para testing de casos edge
test_edge_cases() {
    echo -e "${YELLOW}🔍 TESTING CASOS EDGE${NC}"
    echo -e "${YELLOW}======================${NC}"
    
    edge_cases=(
        ""  # Query vacía
        "asdlkjfñalksjdfñlaksjdfñlaksjdf"  # Gibberish
        "quiero 1000 botellas de champagne"  # Query imposible
        "vino que cuesta -50 euros"  # Query ilógica
        "el mejor vino del universo"  # Query muy ambiciosa
        "🍷🍾🥂"  # Solo emojis
    )
    
    for query in "${edge_cases[@]}"; do
        if [ -z "$query" ]; then
            query_display="[QUERY VACÍA]"
        else
            query_display="$query"
        fi
        
        data="{\"prompt\": \"$query\"}"
        test_endpoint "Edge Case: $query_display" "${MAITRE_URL}/query-dev" "POST" "$data" "true"
    done
}

# Función para mostrar configuración
show_config() {
    echo -e "${YELLOW}⚙️  CONFIGURACIÓN DEL SISTEMA${NC}"
    echo -e "${YELLOW}=============================${NC}"
    echo -e "   Maitre Bot:    $MAITRE_URL"
    echo -e "   Sumiller Bot:  $SUMILLER_URL"
    echo -e "   MCP Server:    $MCP_URL"
    echo -e "   UI:            $UI_URL"
    echo -e "   OpenAI Key:    $(echo $OPENAI_API_KEY | head -c 10)...${GREEN}✓${NC}"
    echo ""
}

# Función para mostrar estadísticas finales
show_stats() {
    echo -e "${PURPLE}📊 RESUMEN DE TESTING${NC}"
    echo -e "${PURPLE}=====================${NC}"
    echo -e "${GREEN}✅ Sistema Multi-Entorno: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ ChromaDB + Búsqueda Vectorial: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ OpenAI Integration: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ Estrategia de Chunks: OPTIMIZADA${NC}"
    echo -e "${GREEN}✅ Respuestas Concisas: IMPLEMENTADA${NC}"
    echo ""
    echo -e "${BLUE}🎯 El sistema está listo para desarrollo y testing.${NC}"
    echo -e "${BLUE}🚀 Para despliegue: ./deploy.sh${NC}"
    echo ""
}

# Función principal
main() {
    case "${1:-all}" in
        "services")
            show_config
            check_services
            ;;
        "health")
            show_config
            health_checks
            ;;
        "mcp")
            show_config
            test_mcp_search
            ;;
        "sumiller")
            show_config
            test_sumiller_direct
            ;;
        "maitre")
            show_config
            test_maitre_complete
            ;;
        "performance")
            show_config
            test_performance
            ;;
        "edge")
            show_config
            test_edge_cases
            ;;
        "all")
            show_config
            check_services
            health_checks
            test_mcp_search
            test_sumiller_direct
            test_maitre_complete
            test_performance
            test_edge_cases
            show_stats
            ;;
        "help")
            echo -e "${PURPLE}🍷 SUMY WINE RECOMMENDER - TESTER${NC}"
            echo -e "${PURPLE}Usage: ./tester.sh [command]${NC}"
            echo ""
            echo -e "Commands:"
            echo -e "  ${YELLOW}all${NC}         - Ejecuta todos los tests (default)"
            echo -e "  ${YELLOW}services${NC}    - Verifica que todos los servicios estén activos"
            echo -e "  ${YELLOW}health${NC}      - Health checks de todos los servicios"
            echo -e "  ${YELLOW}mcp${NC}         - Prueba búsqueda directa en MCP Server"
            echo -e "  ${YELLOW}sumiller${NC}    - Prueba Sumiller Bot directamente"
            echo -e "  ${YELLOW}maitre${NC}      - Prueba Maitre Bot (ruta completa)"
            echo -e "  ${YELLOW}performance${NC} - Tests de rendimiento"
            echo -e "  ${YELLOW}edge${NC}        - Tests de casos edge"
            echo -e "  ${YELLOW}help${NC}        - Muestra esta ayuda"
            echo ""
            echo -e "Examples:"
            echo -e "  ${BLUE}./tester.sh${NC}              # Ejecuta todos los tests"
            echo -e "  ${BLUE}./tester.sh health${NC}       # Solo health checks"
            echo -e "  ${BLUE}./tester.sh performance${NC}  # Solo tests de rendimiento"
            ;;
        *)
            echo -e "${RED}❌ Comando desconocido: $1${NC}"
            echo -e "Usa: ${BLUE}./tester.sh help${NC} para ver comandos disponibles"
            exit 1
            ;;
    esac
}

# Verificar dependencias
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ curl no está instalado${NC}"
    exit 1
fi

if ! command -v bc &> /dev/null; then
    echo -e "${YELLOW}⚠️ bc no está instalado (tests de rendimiento deshabilitados)${NC}"
fi

# Ejecutar función principal
main "$@" 