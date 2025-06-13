#!/bin/bash

# 🍷 PRUEBAS CURL COMPLETAS - SISTEMA SUMILLER MULTI-AGENTE
# ========================================================
# Script con comandos curl para probar TODAS las funcionalidades
# Úsalo copiando y pegando comandos individuales o ejecutando todo

set -e

# 🔗 URLs de los servicios
SUMILLER_URL="https://sumiller-bot-production.up.railway.app"
RAG_URL="https://rag-mcp-server-production.up.railway.app"
MEMORY_URL="https://memory-mcp-server-production.up.railway.app"

# 🎨 Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🍷 =============================================="
echo -e "   PRUEBAS CURL SISTEMA SUMILLER COMPLETO"
echo -e "🍷 ==============================================${NC}"
echo ""

# ============================================================================
# A. HEALTH CHECKS - VERIFICAR QUE TODOS LOS SERVICIOS ESTÁN VIVOS
# ============================================================================

echo -e "${CYAN}📋 A. HEALTH CHECKS${NC}"
echo "--------------------"

echo -e "${BLUE}A1. Health Check - Sumiller Bot Principal${NC}"
echo "curl -s '$SUMILLER_URL/health' | jq ."
curl -s "$SUMILLER_URL/health" | jq .
echo ""

echo -e "${BLUE}A2. Health Check - RAG MCP Server${NC}"
echo "curl -s '$RAG_URL/health' | jq ."
curl -s "$RAG_URL/health" | jq . 2>/dev/null || echo "❌ RAG Server no disponible"
echo ""

echo -e "${BLUE}A3. Health Check - Memory MCP Server${NC}"
echo "curl -s '$MEMORY_URL/health' | jq ."
curl -s "$MEMORY_URL/health" | jq . 2>/dev/null || echo "❌ Memory Server no disponible"
echo ""

# ============================================================================
# B. CLASIFICACIÓN INTELIGENTE - FILTRO LLM
# ============================================================================

echo -e "${CYAN}🧠 B. CLASIFICACIÓN INTELIGENTE${NC}"
echo "--------------------------------"

echo -e "${BLUE}B1. Clasificar Consulta de Vinos${NC}"
echo "curl -X POST '$SUMILLER_URL/classify' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Recomiéndame un vino tinto español para cordero\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un vino tinto español para cordero", "user_id": "test_user"}' | jq .
echo ""

echo -e "${BLUE}B2. Clasificar Consulta Off-Topic${NC}"
echo "curl -X POST '$SUMILLER_URL/classify' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"¿Cuál es la capital de Francia?\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Cuál es la capital de Francia?", "user_id": "test_user"}' | jq .
echo ""

echo -e "${BLUE}B3. Clasificar Mensaje Secreto${NC}"
echo "curl -X POST '$SUMILLER_URL/classify' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Pedro y Vicky tienen un mensaje secreto\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Pedro y Vicky tienen un mensaje secreto", "user_id": "test_user"}' | jq .
echo ""

# ============================================================================
# C. CONSULTAS PRINCIPALES - ENDPOINT /query
# ============================================================================

echo -e "${CYAN}🍷 C. CONSULTAS PRINCIPALES${NC}"
echo "-----------------------------"

echo -e "${BLUE}C1. Consulta Simple de Vinos${NC}"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Necesito un vino para una cena romántica\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Necesito un vino para una cena romántica", "user_id": "test_user"}' | jq .
echo ""

echo -e "${BLUE}C2. Consulta Específica - Vinos Tintos Españoles${NC}"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"¿Qué vino tinto español me recomiendas para cordero asado?\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino tinto español me recomiendas para cordero asado?", "user_id": "test_user"}' | jq .
echo ""

echo -e "${BLUE}C3. Consulta con Presupuesto${NC}"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Vino blanco de menos de 20 euros para mariscos\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Vino blanco de menos de 20 euros para mariscos", "user_id": "test_user"}' | jq .
echo ""

echo -e "${BLUE}C4. Consulta Off-Topic (Debería Redirigir)${NC}"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"¿Cómo está el tiempo hoy?\", \"user_id\": \"test_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Cómo está el tiempo hoy?", "user_id": "test_user"}' | jq .
echo ""

# ============================================================================
# D. RAG MCP SERVER - BÚSQUEDAS DIRECTAS
# ============================================================================

echo -e "${CYAN}🔍 D. RAG MCP SERVER${NC}"
echo "---------------------"

echo -e "${BLUE}D1. Búsqueda RAG Directa - Vinos${NC}"
echo "curl -X POST '$RAG_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"vinos tintos Rioja\", \"max_results\": 3}' | jq ."
curl -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "vinos tintos Rioja", "max_results": 3}' | jq . 2>/dev/null || echo "❌ RAG Server no disponible"
echo ""

echo -e "${BLUE}D2. Búsqueda RAG - Teoría Sumiller${NC}"
echo "curl -X POST '$RAG_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"maridaje carnes rojas\", \"max_results\": 2}' | jq ."
curl -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "maridaje carnes rojas", "max_results": 2}' | jq . 2>/dev/null || echo "❌ RAG Server no disponible"
echo ""

echo -e "${BLUE}D3. Estadísticas RAG Server${NC}"
echo "curl -s '$RAG_URL/stats' | jq ."
curl -s "$RAG_URL/stats" | jq . 2>/dev/null || echo "❌ RAG Stats no disponibles"
echo ""

# ============================================================================
# E. MEMORY MCP SERVER - GESTIÓN DE MEMORIA
# ============================================================================

echo -e "${CYAN}🧠 E. MEMORY MCP SERVER${NC}"
echo "-------------------------"

echo -e "${BLUE}E1. Guardar Interacción en Memoria${NC}"
echo "curl -X POST '$MEMORY_URL/memory/save' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"user_id\": \"test_user\", \"interaction\": {\"query\": \"Test query\", \"response\": \"Test response\", \"timestamp\": \"auto\"}}' | jq ."
curl -X POST "$MEMORY_URL/memory/save" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "interaction": {"query": "Test query", "response": "Test response", "timestamp": "auto"}}' | jq . 2>/dev/null || echo "❌ Memory Server no disponible"
echo ""

echo -e "${BLUE}E2. Recuperar Memoria de Usuario${NC}"
echo "curl -s '$MEMORY_URL/memory/test_user' | jq ."
curl -s "$MEMORY_URL/memory/test_user" | jq . 2>/dev/null || echo "❌ Memory Server no disponible"
echo ""

echo -e "${BLUE}E3. Estadísticas Memory Server${NC}"
echo "curl -s '$MEMORY_URL/stats' | jq ."
curl -s "$MEMORY_URL/stats" | jq . 2>/dev/null || echo "❌ Memory Stats no disponibles"
echo ""

# ============================================================================
# F. ESTADÍSTICAS Y MONITOREO
# ============================================================================

echo -e "${CYAN}📊 F. ESTADÍSTICAS Y MONITOREO${NC}"
echo "--------------------------------"

echo -e "${BLUE}F1. Estadísticas Completas del Sistema${NC}"
echo "curl -s '$SUMILLER_URL/stats' | jq ."
curl -s "$SUMILLER_URL/stats" | jq .
echo ""

echo -e "${BLUE}F2. Estado del Circuit Breaker${NC}"
echo "curl -s '$SUMILLER_URL/health' | jq '.circuit_breaker'"
curl -s "$SUMILLER_URL/health" | jq '.circuit_breaker'
echo ""

echo -e "${BLUE}F3. Configuración del Sistema${NC}"
echo "curl -s '$SUMILLER_URL/health' | jq '.config'"
curl -s "$SUMILLER_URL/health" | jq '.config'
echo ""

# ============================================================================
# G. CASOS DE USO AVANZADOS
# ============================================================================

echo -e "${CYAN}🎯 G. CASOS DE USO AVANZADOS${NC}"
echo "------------------------------"

echo -e "${BLUE}G1. Conversación Multi-Turno${NC}"
echo "# Primera consulta"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Recomiéndame un vino para pasta\", \"user_id\": \"advanced_user\"}' | jq '.response'"
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un vino para pasta", "user_id": "advanced_user"}' | jq '.response'
echo ""

echo "# Segunda consulta (debería recordar contexto)"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"¿Y si la pasta tiene salsa de tomate?\", \"user_id\": \"advanced_user\"}' | jq '.response'"
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Y si la pasta tiene salsa de tomate?", "user_id": "advanced_user"}' | jq '.response'
echo ""

echo -e "${BLUE}G2. Consulta con Restricciones Múltiples${NC}"
echo "curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Vino tinto español, menos de 25 euros, para carne de caza, crianza en barrica\", \"user_id\": \"advanced_user\"}' | jq ."
curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Vino tinto español, menos de 25 euros, para carne de caza, crianza en barrica", "user_id": "advanced_user"}' | jq .
echo ""

# ============================================================================
# H. PRUEBAS DE RENDIMIENTO Y LÍMITES
# ============================================================================

echo -e "${CYAN}⚡ H. PRUEBAS DE RENDIMIENTO${NC}"
echo "-----------------------------"

echo -e "${BLUE}H1. Consulta Rápida (Medir Tiempo)${NC}"
echo "time curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Vino rápido\", \"user_id\": \"speed_test\"}' | jq '.query_category'"
time curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Vino rápido", "user_id": "speed_test"}' | jq '.query_category'
echo ""

echo -e "${BLUE}H2. Consulta Compleja (Medir Tiempo)${NC}"
echo "time curl -X POST '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Necesito una recomendación muy específica de vino tinto español de la región de Rioja, con crianza en barrica de roble francés, que tenga entre 3-5 años de envejecimiento, con un precio entre 15 y 30 euros, que maride perfectamente con cordero asado con hierbas mediterráneas, para una cena especial de aniversario\", \"user_id\": \"complex_test\"}' | jq '.wines_found'"
time curl -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Necesito una recomendación muy específica de vino tinto español de la región de Rioja, con crianza en barrica de roble francés, que tenga entre 3-5 años de envejecimiento, con un precio entre 15 y 30 euros, que maride perfectamente con cordero asado con hierbas mediterráneas, para una cena especial de aniversario", "user_id": "complex_test"}' | jq '.wines_found'
echo ""

# ============================================================================
# I. COMANDOS ÚTILES PARA DEBUGGING
# ============================================================================

echo -e "${CYAN}🔧 I. COMANDOS DE DEBUGGING${NC}"
echo "-----------------------------"

echo -e "${BLUE}I1. Solo Headers (Verificar Conectividad)${NC}"
echo "curl -I '$SUMILLER_URL/health'"
echo ""

echo -e "${BLUE}I2. Verbose (Ver Detalles de Conexión)${NC}"
echo "curl -v '$SUMILLER_URL/health' 2>&1 | head -20"
echo ""

echo -e "${BLUE}I3. Timeout Personalizado${NC}"
echo "curl --max-time 5 '$SUMILLER_URL/query' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"test\", \"user_id\": \"timeout_test\"}'"
echo ""

# ============================================================================
# J. RESUMEN Y COMANDOS PARA COPIAR-PEGAR
# ============================================================================

echo -e "${CYAN}📋 J. COMANDOS RÁPIDOS PARA COPIAR-PEGAR${NC}"
echo "--------------------------------------------"

echo -e "${YELLOW}# Quick Health Check:"
echo "curl -s '$SUMILLER_URL/health' | jq '.status, .services'"
echo ""

echo -e "${YELLOW}# Quick Wine Query:"
echo "curl -X POST '$SUMILLER_URL/query' -H 'Content-Type: application/json' -d '{\"prompt\": \"vino tinto español\", \"user_id\": \"quick_test\"}' | jq '.response, .wines_found, .used_rag'"
echo ""

echo -e "${YELLOW}# Quick Classification Test:"
echo "curl -X POST '$SUMILLER_URL/classify' -H 'Content-Type: application/json' -d '{\"prompt\": \"¿Qué es la fotosíntesis?\", \"user_id\": \"test\"}' | jq '.classification.category'"
echo ""

echo -e "${GREEN}✅ ¡PRUEBAS COMPLETAS TERMINADAS!${NC}"
echo -e "${GREEN}📋 Usa estos comandos individuales para probar funcionalidades específicas${NC}"
echo -e "${GREEN}🔄 Ejecuta todo el script con: ./test_curl_completo.sh${NC}"
echo "" 