#!/bin/bash

# 🔍 TEST ESPECÍFICO PARA BASE DE DATOS DE EMBEDDINGS
# ===================================================
# Verifica si el sistema está consultando correctamente ChromaDB

set -e

# URLs
SUMILLER_URL="https://sumiller-bot-production.up.railway.app"
RAG_URL="https://rag-mcp-server-production.up.railway.app"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🔍 =============================================="
echo -e "   TEST EMBEDDINGS - BASE DE DATOS VECTORIAL"
echo -e "🔍 ==============================================${NC}"
echo ""

# ============================================================================
# 1. VERIFICAR QUE RAG SERVER ESTÁ USANDO EMBEDDINGS
# ============================================================================

echo -e "${BLUE}📊 1. VERIFICAR ESTADO DEL RAG SERVER${NC}"
echo "------------------------------------"

echo "Consultando health del RAG server..."
RAG_HEALTH=$(curl -s "$RAG_URL/health" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ RAG Server está respondiendo${NC}"
    echo "$RAG_HEALTH" | jq '.'
else
    echo -e "${RED}❌ RAG Server no está disponible${NC}"
    echo "El test de embeddings requiere que el RAG server esté funcionando"
    exit 1
fi
echo ""

# ============================================================================
# 2. TEST DIRECTO AL RAG - CONSULTA QUE DEBERÍA ENCONTRAR VINOS ESPECÍFICOS
# ============================================================================

echo -e "${BLUE}🍷 2. TEST DIRECTO RAG - BUSCAR VINOS ESPECÍFICOS${NC}"
echo "-----------------------------------------------"

echo "Buscando vinos de 'Rioja' directamente en el RAG..."
RAG_RESPONSE=$(curl -s -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "vinos de Rioja tinto", "max_results": 3}' 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$RAG_RESPONSE" ]; then
    echo -e "${GREEN}✅ RAG Server respondió${NC}"
    
    # Verificar si encontró vinos
    SOURCES_COUNT=$(echo "$RAG_RESPONSE" | jq '.sources | length' 2>/dev/null || echo "0")
    echo "Número de vinos encontrados: $SOURCES_COUNT"
    
    if [ "$SOURCES_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ EMBEDDINGS FUNCIONANDO: Encontró $SOURCES_COUNT vinos${NC}"
        echo "Primeros resultados:"
        echo "$RAG_RESPONSE" | jq '.sources[0:2][] | {name: .metadata.name, region: .metadata.region, type: .metadata.type}'
    else
        echo -e "${RED}❌ NO SE ENCONTRARON VINOS: Posible problema con embeddings${NC}"
    fi
else
    echo -e "${RED}❌ Error consultando RAG server directamente${NC}"
fi
echo ""

# ============================================================================
# 3. TEST SUMILLER CON CONSULTA QUE REQUIERE EMBEDDINGS
# ============================================================================

echo -e "${BLUE}🧠 3. TEST SUMILLER - CONSULTA QUE REQUIERE BÚSQUEDA VECTORIAL${NC}"
echo "------------------------------------------------------------"

echo "Consultando al sumiller sobre vinos específicos que requieren embeddings..."
SUMILLER_RESPONSE=$(curl -s -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un vino tinto de la Ribera del Duero con notas de cereza", "user_id": "embedding_test"}')

if [ $? -eq 0 ] && [ -n "$SUMILLER_RESPONSE" ]; then
    echo -e "${GREEN}✅ Sumiller respondió${NC}"
    
    # Verificar si usó RAG
    USED_RAG=$(echo "$SUMILLER_RESPONSE" | jq '.used_rag' 2>/dev/null)
    WINES_FOUND=$(echo "$SUMILLER_RESPONSE" | jq '.wines_found' 2>/dev/null || echo "0")
    CATEGORY=$(echo "$SUMILLER_RESPONSE" | jq -r '.query_category' 2>/dev/null)
    
    echo "¿Usó RAG?: $USED_RAG"
    echo "Vinos encontrados: $WINES_FOUND"
    echo "Categoría: $CATEGORY"
    
    if [ "$USED_RAG" = "true" ] && [ "$WINES_FOUND" -gt 0 ]; then
        echo -e "${GREEN}✅ EMBEDDINGS ACTIVOS: Sumiller usó RAG y encontró $WINES_FOUND vinos${NC}"
    elif [ "$USED_RAG" = "true" ] && [ "$WINES_FOUND" = "0" ]; then
        echo -e "${YELLOW}⚠️  RAG USADO PERO SIN RESULTADOS: Posible problema con embeddings${NC}"
    elif [ "$USED_RAG" = "false" ]; then
        echo -e "${RED}❌ RAG NO USADO: El sumiller no consultó la base de embeddings${NC}"
    fi
    
    echo ""
    echo "Respuesta del sumiller:"
    echo "$SUMILLER_RESPONSE" | jq -r '.response' | head -c 200
    echo "..."
else
    echo -e "${RED}❌ Error consultando al sumiller${NC}"
fi
echo ""

# ============================================================================
# 4. TEST COMPARATIVO - CONSULTA GENÉRICA VS ESPECÍFICA
# ============================================================================

echo -e "${BLUE}📈 4. TEST COMPARATIVO - GENÉRICA VS ESPECÍFICA${NC}"
echo "----------------------------------------------"

echo "Test 1: Consulta genérica (puede no usar embeddings)..."
GENERIC_RESPONSE=$(curl -s -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un vino", "user_id": "generic_test"}')

GENERIC_USED_RAG=$(echo "$GENERIC_RESPONSE" | jq '.used_rag' 2>/dev/null)
GENERIC_WINES=$(echo "$GENERIC_RESPONSE" | jq '.wines_found' 2>/dev/null || echo "0")

echo "Consulta genérica - Usó RAG: $GENERIC_USED_RAG, Vinos: $GENERIC_WINES"

echo ""
echo "Test 2: Consulta muy específica (debería usar embeddings)..."
SPECIFIC_RESPONSE=$(curl -s -X POST "$SUMILLER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Busco un vino tinto español de Jumilla con denominación de origen, crianza en barrica de roble, que maride con cordero lechal", "user_id": "specific_test"}')

SPECIFIC_USED_RAG=$(echo "$SPECIFIC_RESPONSE" | jq '.used_rag' 2>/dev/null)
SPECIFIC_WINES=$(echo "$SPECIFIC_RESPONSE" | jq '.wines_found' 2>/dev/null || echo "0")

echo "Consulta específica - Usó RAG: $SPECIFIC_USED_RAG, Vinos: $SPECIFIC_WINES"

if [ "$SPECIFIC_USED_RAG" = "true" ] && [ "$SPECIFIC_WINES" -gt 0 ]; then
    echo -e "${GREEN}✅ EMBEDDINGS FUNCIONANDO CORRECTAMENTE${NC}"
elif [ "$SPECIFIC_USED_RAG" = "true" ] && [ "$SPECIFIC_WINES" = "0" ]; then
    echo -e "${YELLOW}⚠️  EMBEDDINGS FUNCIONAN PERO NO ENCUENTRAN COINCIDENCIAS${NC}"
else
    echo -e "${RED}❌ PROBLEMA: Consulta específica no usa embeddings${NC}"
fi
echo ""

# ============================================================================
# 5. TEST DE BÚSQUEDA SEMÁNTICA - PALABRAS RELACIONADAS
# ============================================================================

echo -e "${BLUE}🔗 5. TEST BÚSQUEDA SEMÁNTICA - PALABRAS RELACIONADAS${NC}"
echo "-----------------------------------------------------"

echo "Probando si los embeddings capturan relaciones semánticas..."

# Buscar con sinónimos/palabras relacionadas
echo "Búsqueda con 'maridaje'..."
SEMANTIC_RESPONSE=$(curl -s -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "maridaje carne roja", "max_results": 2}' 2>/dev/null)

SEMANTIC_SOURCES=$(echo "$SEMANTIC_RESPONSE" | jq '.sources | length' 2>/dev/null || echo "0")
echo "Resultados para 'maridaje': $SEMANTIC_SOURCES"

echo "Búsqueda con 'acompañar'..."
SEMANTIC_RESPONSE2=$(curl -s -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "acompañar carne roja", "max_results": 2}' 2>/dev/null)

SEMANTIC_SOURCES2=$(echo "$SEMANTIC_RESPONSE2" | jq '.sources | length' 2>/dev/null || echo "0")
echo "Resultados para 'acompañar': $SEMANTIC_SOURCES2"

if [ "$SEMANTIC_SOURCES" -gt 0 ] || [ "$SEMANTIC_SOURCES2" -gt 0 ]; then
    echo -e "${GREEN}✅ BÚSQUEDA SEMÁNTICA FUNCIONA: Los embeddings capturan relaciones${NC}"
else
    echo -e "${YELLOW}⚠️  BÚSQUEDA SEMÁNTICA LIMITADA: Revisar modelo de embeddings${NC}"
fi
echo ""

# ============================================================================
# 6. DIAGNÓSTICO FINAL
# ============================================================================

echo -e "${PURPLE}📊 6. DIAGNÓSTICO FINAL DE EMBEDDINGS${NC}"
echo "======================================"

# Contar tests exitosos
TESTS_PASSED=0
TOTAL_TESTS=4

# Test 1: RAG responde
if [ "$SOURCES_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Test 1: RAG encuentra vinos específicos${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Test 1: RAG no encuentra vinos específicos${NC}"
fi

# Test 2: Sumiller usa RAG
if [ "$USED_RAG" = "true" ]; then
    echo -e "${GREEN}✅ Test 2: Sumiller usa base de embeddings${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Test 2: Sumiller no usa base de embeddings${NC}"
fi

# Test 3: Consulta específica vs genérica
if [ "$SPECIFIC_USED_RAG" = "true" ] && [ "$SPECIFIC_WINES" -gt 0 ]; then
    echo -e "${GREEN}✅ Test 3: Consultas específicas activan embeddings${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Test 3: Consultas específicas no activan embeddings${NC}"
fi

# Test 4: Búsqueda semántica
if [ "$SEMANTIC_SOURCES" -gt 0 ] || [ "$SEMANTIC_SOURCES2" -gt 0 ]; then
    echo -e "${GREEN}✅ Test 4: Búsqueda semántica funciona${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Test 4: Búsqueda semántica no funciona${NC}"
fi

echo ""
echo "RESULTADO FINAL: $TESTS_PASSED/$TOTAL_TESTS tests exitosos"

if [ "$TESTS_PASSED" -eq "$TOTAL_TESTS" ]; then
    echo -e "${GREEN}🎉 EMBEDDINGS FUNCIONANDO PERFECTAMENTE${NC}"
elif [ "$TESTS_PASSED" -ge 2 ]; then
    echo -e "${YELLOW}⚠️  EMBEDDINGS FUNCIONANDO PARCIALMENTE${NC}"
else
    echo -e "${RED}❌ PROBLEMA CON EMBEDDINGS - REQUIERE INVESTIGACIÓN${NC}"
fi

echo ""
echo -e "${BLUE}💡 COMANDOS ÚTILES PARA DEBUGGING:${NC}"
echo "curl -s '$RAG_URL/stats' | jq ."
echo "curl -s '$SUMILLER_URL/health' | jq '.services.rag_mcp'"
echo "" 