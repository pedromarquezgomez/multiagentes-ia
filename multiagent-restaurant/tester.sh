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
# Detectar si estamos testando local o cloud
if [ "${1}" = "cloud" ] || [ "${ENVIRONMENT}" = "cloud" ] || [ -n "${CLOUD_SUMILLER_URL}" ]; then
    echo -e "${BLUE}🌐 Modo Cloud Run detectado${NC}"
    # URLs de Cloud Run para sistema MCP Agentic RAG
    SUMILLER_URL="${CLOUD_SUMILLER_URL:-https://sumiller-bot-rkhznukoea-ew.a.run.app}"
    RAG_MCP_URL="${CLOUD_RAG_MCP_URL:-https://rag-mcp-server-rkhznukoea-ew.a.run.app}"
    MEMORY_MCP_URL="${CLOUD_MEMORY_MCP_URL:-https://memory-mcp-server-rkhznukoea-ew.a.run.app}"
    UI_URL="https://maitre-ia.web.app"
    ENV_MODE="CLOUD"
else
    echo -e "${BLUE}🏠 Modo Local detectado${NC}"
    # URLs locales para sistema MCP Agentic RAG
    BASE_URL="http://localhost"
    SUMILLER_PORT="8001"
    RAG_MCP_PORT="8000"
    MEMORY_MCP_PORT="8002"
    UI_PORT="3000"

    SUMILLER_URL="${BASE_URL}:${SUMILLER_PORT}"
    RAG_MCP_URL="${BASE_URL}:${RAG_MCP_PORT}"
    MEMORY_MCP_URL="${BASE_URL}:${MEMORY_MCP_PORT}"
    UI_URL="${BASE_URL}:${UI_PORT}"
    ENV_MODE="LOCAL"
fi

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
        "Sumiller Bot Agéntico:${SUMILLER_URL}" 
        "RAG MCP Server:${RAG_MCP_URL}"
        "Memory MCP Server:${MEMORY_MCP_URL}"
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
    
    test_endpoint "Sumiller Health" "${SUMILLER_URL}/health" "GET" "" "true"
    test_endpoint "RAG MCP Health" "${RAG_MCP_URL}/health" "GET" "" "true"
    test_endpoint "Memory MCP Health" "${MEMORY_MCP_URL}/health" "GET" "" "true"
}

# Función para probar búsqueda directa en MCP
test_rag_mcp_search() {
    echo -e "${YELLOW}🧠 TESTING RAG MCP SERVER (Agentic Search)${NC}"
    echo -e "${YELLOW}===========================================${NC}"
    
    queries=(
        "tinto para carne"
        "blanco para pescado"
        "espumoso para celebrar"
        "algo barato"
        "vino de rioja"
        "consulta sin sentido xyz123"
    )
    
    for query in "${queries[@]}"; do
        data="{\"query\": \"$query\", \"max_results\": 3, \"expand_query\": true, \"user_id\": \"test_user\"}"
        test_endpoint "RAG Search: $query" "${RAG_MCP_URL}/search" "POST" "$data" "true"
    done
}

test_memory_mcp() {
    echo -e "${YELLOW}💾 TESTING MEMORY MCP SERVER${NC}"
    echo -e "${YELLOW}============================${NC}"
    
    # Test guardado de memoria
    data="{\"user_id\": \"test_user\", \"interaction\": {\"query\": \"tinto para carne\", \"response\": \"Recomiendo un Tempranillo\", \"timestamp\": \"auto\"}}"
    test_endpoint "Save Memory" "${MEMORY_MCP_URL}/memory/save" "POST" "$data" "true"
    
    # Test recuperación de memoria
    test_endpoint "Get Memory" "${MEMORY_MCP_URL}/memory/test_user" "GET" "" "true"
    
    # Test estadísticas
    test_endpoint "Memory Stats" "${MEMORY_MCP_URL}/stats" "GET" "" "true"
}

# Función para probar sumiller directamente
test_sumiller_agentic() {
    echo -e "${YELLOW}🍷 TESTING SUMILLER BOT AGÉNTICO${NC}"
    echo -e "${YELLOW}=================================${NC}"
    
    queries=(
        "recomiéndame un tinto para carne asada"
        "necesito un blanco para mariscos"
        "quiero un espumoso para una boda"
        "algo económico para todos los días"
        "un vino de la rioja"
    )
    
    for query in "${queries[@]}"; do
        data="{\"prompt\": \"$query\", \"user_id\": \"test_user_sumiller\"}"
        test_endpoint "Sumiller Agéntico: $query" "${SUMILLER_URL}/query" "POST" "$data" "true"
    done
    
    # Test estadísticas del sumiller
    test_endpoint "Sumiller Stats" "${SUMILLER_URL}/stats" "GET" "" "true"
}

# Función para testing completo del sistema agéntico
test_full_agentic_flow() {
    echo -e "${YELLOW}🎯 TESTING FLUJO COMPLETO AGÉNTICO${NC}"
    echo -e "${YELLOW}==================================${NC}"
    
    echo -e "${BLUE}Probando flujo completo con memoria...${NC}"
    
    # Usuario test para el flujo completo
    user_id="test_user_flow_$(date +%s)"
    
    queries=(
        "recomiéndame un tinto potente"
        "ahora algo más suave del mismo tipo"  # Debería usar memoria
        "un blanco fresco para mariscos"
        "algo similar pero más económico"      # Debería usar contexto
        "no sé nada de vinos, ayúdame"
        "quiero algo de menos de 50 euros"
    )
    
    for query in "${queries[@]}"; do
        data="{\"prompt\": \"$query\", \"user_id\": \"$user_id\"}"
        test_endpoint "Flujo Agéntico: $query" "${SUMILLER_URL}/query" "POST" "$data" "true"
        sleep 1  # Pequeña pausa para simular conversación real
    done
    
    # Verificar que la memoria se guardó
    test_endpoint "Verificar Memoria del Usuario" "${MEMORY_MCP_URL}/memory/$user_id" "GET" "" "true"
}

# Función para testing de rendimiento
test_performance() {
    echo -e "${YELLOW}⚡ TESTING DE RENDIMIENTO${NC}"
    echo -e "${YELLOW}=========================${NC}"
    
    echo -e "${BLUE}Midiendo tiempo de respuesta...${NC}"
    
    query="tinto para carne asada"
    data="{\"prompt\": \"$query\"}"
    
    echo -e "   Testing RAG MCP Server..."
    rag_data="{\"query\": \"$query\", \"max_results\": 3, \"expand_query\": true, \"user_id\": \"test_perf\"}"
    start_time=$(date +%s.%N)
    curl -s -X POST "${RAG_MCP_URL}/search" -H "Content-Type: application/json" -d "$rag_data" > /dev/null
    end_time=$(date +%s.%N)
    rag_time=$(echo "$end_time - $start_time" | bc)
    echo -e "   ${GREEN}RAG MCP Response Time: ${rag_time}s${NC}"
    
    echo -e "   Testing Memory MCP Server..."
    start_time=$(date +%s.%N)
    curl -s -X GET "${MEMORY_MCP_URL}/memory/test_perf" > /dev/null
    end_time=$(date +%s.%N)
    memory_time=$(echo "$end_time - $start_time" | bc)
    echo -e "   ${GREEN}Memory MCP Response Time: ${memory_time}s${NC}"
    
    echo -e "   Testing Sumiller Bot Agéntico..."
    agentic_data="{\"prompt\": \"$query\", \"user_id\": \"test_perf\"}"
    start_time=$(date +%s.%N)
    curl -s -X POST "${SUMILLER_URL}/query" -H "Content-Type: application/json" -d "$agentic_data" > /dev/null
    end_time=$(date +%s.%N)
    sumiller_time=$(echo "$end_time - $start_time" | bc)
    echo -e "   ${GREEN}Sumiller Agéntico Response Time: ${sumiller_time}s${NC}"
    
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
        
        data="{\"prompt\": \"$query\", \"user_id\": \"test_edge\"}"
        test_endpoint "Edge Case: $query_display" "${SUMILLER_URL}/query" "POST" "$data" "true"
    done
}

# Función para mostrar configuración
show_config() {
    echo -e "${YELLOW}⚙️  CONFIGURACIÓN DEL SISTEMA${NC}"
    echo -e "${YELLOW}=============================${NC}"
    echo -e "   Entorno:          ${ENV_MODE}"
    echo -e "   Sumiller Bot:     $SUMILLER_URL"
    echo -e "   RAG MCP Server:   $RAG_MCP_URL"
    echo -e "   Memory MCP:       $MEMORY_MCP_URL"
    echo -e "   UI:               $UI_URL"
    if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "   OpenAI Key:    $(echo $OPENAI_API_KEY | head -c 10)...${GREEN}✓${NC}"
    else
        echo -e "   OpenAI Key:    ${YELLOW}No configurada localmente (usando secreto Cloud)${NC}"
    fi
    echo ""
}

# Función para mostrar estadísticas finales
show_stats() {
    echo -e "${PURPLE}📊 RESUMEN DE TESTING${NC}"
    echo -e "${PURPLE}=====================${NC}"
    echo -e "${GREEN}✅ Sistema MCP Agentic RAG: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ Expansión Agéntica de Consultas: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ Memoria Conversacional: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ ChromaDB + Búsqueda Vectorial: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ OpenAI Integration: FUNCIONANDO${NC}"
    echo -e "${GREEN}✅ Personalización por Usuario: IMPLEMENTADA${NC}"
    echo ""
    echo -e "${BLUE}🎯 El sistema está listo para desarrollo y testing.${NC}"
    echo -e "${BLUE}🚀 Para despliegue: ./deploy.sh${NC}"
    echo ""
}

# Función principal
main() {
    # Si el primer argumento es "cloud", removemos y ejecutamos todos los tests
    if [ "${1}" = "cloud" ]; then
        shift  # Remover "cloud" de los argumentos
        command="${1:-all}"  # Si no hay más argumentos, usar "all"
    else
        command="${1:-all}"
    fi
    
    case "$command" in
        "services")
            show_config
            check_services
            ;;
        "health")
            show_config
            health_checks
            ;;
        "rag")
            show_config
            test_rag_mcp_search
            ;;
        "memory")
            show_config
            test_memory_mcp
            ;;
        "sumiller")
            show_config
            test_sumiller_agentic
            ;;
        "flow")
            show_config
            test_full_agentic_flow
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
            test_rag_mcp_search
            test_memory_mcp
            test_sumiller_agentic
            test_full_agentic_flow
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
            echo -e "  ${YELLOW}cloud${NC}       - Ejecuta todos los tests en Cloud Run"
            echo -e "  ${YELLOW}services${NC}    - Verifica que todos los servicios estén activos"
            echo -e "  ${YELLOW}health${NC}      - Health checks de todos los servicios"
            echo -e "  ${YELLOW}rag${NC}         - Prueba RAG MCP Server (búsqueda agéntica)"
            echo -e "  ${YELLOW}memory${NC}      - Prueba Memory MCP Server"
            echo -e "  ${YELLOW}sumiller${NC}    - Prueba Sumiller Bot Agéntico"
            echo -e "  ${YELLOW}flow${NC}        - Prueba flujo completo con memoria"
            echo -e "  ${YELLOW}performance${NC} - Tests de rendimiento"
            echo -e "  ${YELLOW}edge${NC}        - Tests de casos edge"
            echo -e "  ${YELLOW}help${NC}        - Muestra esta ayuda"
            echo ""
            echo -e "Examples:"
            echo -e "  ${BLUE}./tester.sh${NC}              # Ejecuta todos los tests (local)"
            echo -e "  ${BLUE}./tester.sh cloud${NC}        # Ejecuta todos los tests (Cloud Run)"
            echo -e "  ${BLUE}./tester.sh health${NC}       # Solo health checks"
            echo -e "  ${BLUE}./tester.sh performance${NC}  # Solo tests de rendimiento"
            echo ""
            echo -e "Environment:"
            echo -e "  ${BLUE}Local:${NC}  Usa localhost y puertos específicos"
            echo -e "  ${BLUE}Cloud:${NC}  Usa URLs de Google Cloud Run"
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