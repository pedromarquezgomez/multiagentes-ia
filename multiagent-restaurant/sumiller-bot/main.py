# sumiller-bot/main.py
"""
Sumiller Bot - Versión Mejorada con HTTP Connection Pooling y Resilient Client
Código completo actualizado sin errores
"""
import os
import sys
import logging
import json
from openai import AsyncOpenAI
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Importar el nuevo cliente resiliente
from http_client import resilient_client, close_http_pool

# Importar configuración multi-entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# --- Configuración ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del puerto que funciona en local y Cloud Run
PORT = int(os.getenv("PORT", str(config.sumiller_port if config.is_local() else 8080)))

# URLs de los nuevos servicios MCP Agentic RAG
RAG_MCP_URL = os.getenv('RAG_MCP_URL', "http://localhost:8000")
MEMORY_MCP_URL = os.getenv('MEMORY_MCP_URL', "http://localhost:8002")

# Configuración OpenAI
OPENAI_API_KEY = config.get_openai_key()
OPENAI_BASE_URL = config.get_openai_base_url()
OPENAI_MODEL = config.get_openai_model()

if not OPENAI_API_KEY:
    logger.warning("No se pudo obtener la OpenAI API Key. Las llamadas a OpenAI no funcionarán.")
    openai_client = None
else:
    # Usar el cliente OpenAI con la configuración de OpenAI
    openai_client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )
    logger.info(f"✅ Cliente OpenAI configurado: {OPENAI_BASE_URL} - Modelo: {OPENAI_MODEL}")

# 🔄 LIFECYCLE MANAGEMENT MEJORADO
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando Sumiller Bot con HTTP pooling...")
    
    # Verificar conectividad inicial y pre-warm connections
    try:
        client = await resilient_client.pool.get_client()
        # Pre-warm connections con health checks
        try:
            await client.get(f"{RAG_MCP_URL}/health", timeout=5.0)
            logger.info("✅ RAG MCP Server conectado")
        except Exception as e:
            logger.warning(f"⚠️ RAG MCP Server no disponible: {e}")
        
        try:
            await client.get(f"{MEMORY_MCP_URL}/health", timeout=5.0)
            logger.info("✅ Memory MCP Server conectado")
        except Exception as e:
            logger.warning(f"⚠️ Memory MCP Server no disponible: {e}")
            
        logger.info("✅ HTTP pool inicializado y conexiones pre-calentadas")
    except Exception as e:
        logger.warning(f"⚠️ Error durante inicialización: {e}")
    
    yield
    
    # Shutdown
    logger.info("🔒 Cerrando Sumiller Bot...")
    await close_http_pool()
    logger.info("✅ Recursos liberados correctamente")

# Crear app con lifecycle management
app = FastAPI(
    title="Sumiller Bot API - Resilient",
    description="Sumiller con connection pooling, circuit breakers y retry logic",
    version="3.1.0",
    lifespan=lifespan
)

# Configuración de CORS para permitir conexiones desde la UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos (sin cambios) ---
class Query(BaseModel):
    prompt: str
    user_id: str = "default_user"  # Para memoria conversacional

class RecommendationResponse(BaseModel):
    response: str
    expanded_queries: List[str] = []
    wines_found: int = 0

# --- Funciones Mejoradas con Cliente Resiliente ---

async def search_wines_with_agentic_rag(user_query: str, user_id: str = "default_user") -> Dict[str, Any]:
    """
    ✨ VERSIÓN MEJORADA: Utiliza connection pooling y retry logic
    """
    logger.info(f"🔍 Búsqueda RAG resiliente para: '{user_query}'")
    
    try:
        # 1. Obtener contexto de memoria (con retry automático)
        logger.info("💾 Obteniendo contexto de memoria...")
        memory_context = await get_user_memory_resilient(user_id)
        
        # 2. Preparar payload para RAG
        rag_payload = {
            "query": user_query,
            "max_results": 3
        }
        
        if memory_context:
            rag_payload["context"] = memory_context
        
        # 3. 🚀 LLAMADA RESILIENTE CON POOLING
        logger.info(f"📤 Llamada resiliente a {RAG_MCP_URL}/query")
        search_result = await resilient_client.post_with_retry(
            url=f"{RAG_MCP_URL}/query",
            json_data=rag_payload,
            max_retries=3  # Retry automático con backoff
        )
        
        wines_found = len(search_result.get('sources', []))
        logger.info(f"✅ RAG resiliente encontró {wines_found} vinos")
        
        return search_result
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda resiliente: {e}")
        # Fallback graceful
        return await fallback_search_resilient(user_query)

async def get_user_memory_resilient(user_id: str) -> Dict[str, Any]:
    """Obtener memoria con cliente resiliente"""
    try:
        memory_data = await resilient_client.get_with_retry(
            url=f"{MEMORY_MCP_URL}/memory/{user_id}",
            max_retries=2  # Menos retries para memoria (no crítico)
        )
        logger.info(f"💾 Memoria recuperada resiliente para {user_id}")
        return memory_data
    except Exception as e:
        logger.warning(f"⚠️ No se pudo recuperar memoria (no crítico): {e}")
        return {}

async def fallback_search_resilient(user_query: str) -> Dict[str, Any]:
    """Fallback con cliente resiliente"""
    try:
        # Intento más simple con menos parámetros
        result = await resilient_client.post_with_retry(
            url=f"{RAG_MCP_URL}/query",
            json_data={"query": user_query, "max_results": 1},
            max_retries=1
        )
        logger.info("✅ Fallback resiliente exitoso")
        return result
    except Exception as e:
        logger.error(f"❌ Fallback resiliente también falló: {e}")
        return {
            "sources": [], 
            "expanded_queries": [], 
            "error": "Todos los servicios no disponibles"
        }

async def save_user_interaction_resilient(user_id: str, query: str, response: str, wines: List[Dict]) -> None:
    """Guardar interacción con cliente resiliente"""
    try:
        memory_payload = {
            "user_id": user_id,
            "interaction": {
                "query": query,
                "response": response,
                "wines_recommended": [wine.get('metadata', {}).get('name', '') for wine in wines[:3]],
                "timestamp": "auto"
            }
        }
        
        await resilient_client.post_with_retry(
            url=f"{MEMORY_MCP_URL}/memory/save",
            json_data=memory_payload,
            max_retries=2
        )
        logger.info(f"💾 Interacción guardada resiliente para {user_id}")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo guardar en memoria (no crítico): {e}")

async def generate_agentic_response(user_query: str, search_result: Dict[str, Any], user_id: str) -> str:
    """
    Genera una respuesta conversacional usando el contexto completo del RAG agéntico.
    """
    if not openai_client:
        return f"La API de OpenAI no está configurada. Resultados: {json.dumps(search_result.get('sources', []))}"

    documents = search_result.get('sources', [])  # RAG MCP devuelve 'sources' no 'documents'
    expanded_queries = search_result.get('expanded_queries', [])
    
    if not documents:
        system_prompt = """
        Eres Sumy, un sumiller profesional con formación completa en sumillería.
        
        SITUACIÓN: No encontraste vinos específicos, pero puedes ofrecer conocimiento profesional.
        
        RESPUESTA SEGÚN TIPO DE CONSULTA:
        
        A) SI BUSCA TEORÍA/CONOCIMIENTO:
        - Explica el concepto usando tu formación profesional
        - Enseña principios de sumillería relevantes
        - Usa terminología técnica apropiada
        - Ofrece consejos prácticos
        
        B) SI BUSCA VINOS ESPECÍFICOS:
        - Discúlpate por no encontrar vinos exactos
        - Explica qué características debería buscar según principios de maridaje
        - Sugiere términos alternativos basados en tu conocimiento
        - Ofrece principios generales que aplican a su búsqueda
        
        REGLAS:
        - Mantén tono profesional y educativo
        - Siempre aporta valor con conocimiento teórico
        - Usa tu formación para guiar al usuario
        """
        user_content = f"Consulta original: \"{user_query}\"\nConsultas expandidas probadas: {expanded_queries}"
    else:
        system_prompt = """
        Eres Sumy, un sumiller profesional con IA agéntica avanzada y formación completa en sumillería.
        
        CAPACIDADES PROFESIONALES:
        - Dominas los fundamentos del vino (taninos, acidez, aromas, cuerpo)
        - Conoces técnicas de cata profesional (5 sentidos, fases de cata)
        - Aplicas principios de maridaje (intensidad, sabor, textura, acidez)
        - Manejas temperaturas de servicio y conservación
        - Conoces regiones vitivinícolas y sus características
        - Tu sistema expandió la consulta para mejores resultados
        
        TIPOS DE CONSULTA Y RESPUESTA:
        
        A) SALUDOS Y CONVERSACIÓN GENERAL:
        Si la consulta es un saludo, pregunta general, o no especifica vinos:
        - Responde de forma amable y profesional
        - Preséntate brevemente como Sumy, el sumiller virtual
        - Indica en qué puedes ayudar (recomendaciones, maridajes, teoría)
        - NO uses marcadores de estructura
        
        B) CONSULTAS DE TEORÍA/FORMACIÓN:
        [PRINCIPIO]
        Explica conceptos de sumillería con fundamentos teóricos completos
        [/PRINCIPIO]
        
        C) RECOMENDACIONES DE VINOS:
        [PRINCIPIO]
        Explica brevemente el principio o fundamento aplicado (máximo 2 líneas)
        [/PRINCIPIO]

        [RECOMENDACION_1]
        **Nombre del Vino** (Región) - €precio
        Justificación técnica concisa basada en características específicas
        Temperatura de servicio: X°C
        [/RECOMENDACION_1]

        REGLAS ESTRICTAS:
        - Para recomendaciones: SOLO 1 vino (el mejor)
        - Para teoría: usa solo [PRINCIPIO]
        - Para saludos: respuesta natural sin marcadores
        - Cada recomendación debe ser concisa (2-3 líneas máximo)
        - SIEMPRE incluye temperatura de servicio en recomendaciones
        """
        
        # Separar vinos de teoría en los resultados
        wine_docs = [doc for doc in documents if doc.get('metadata', {}).get('doc_type') != 'teoria_sumiller']
        theory_docs = [doc for doc in documents if doc.get('metadata', {}).get('doc_type') == 'teoria_sumiller']
        
        user_content = f"""
        Consulta original: "{user_query}"
        Mi sistema agéntico expandió la búsqueda a: {expanded_queries}
        
        CONOCIMIENTO TEÓRICO RELEVANTE:
        {json.dumps(theory_docs, indent=2, ensure_ascii=False) if theory_docs else "Sin teoría específica encontrada"}
        
        VINOS ENCONTRADOS:
        {json.dumps(wine_docs, indent=2, ensure_ascii=False) if wine_docs else "Sin vinos específicos encontrados"}
        
        INSTRUCCIONES:
        - Si hay teoría relevante, úsala para explicar conceptos y justificar recomendaciones
        - Si hay vinos, explica por qué son adecuados usando principios profesionales
        - Combina ambos para dar una respuesta completa y educativa
        """
    
    try:
        response = await openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error al generar respuesta agéntica con OpenAI: {e}")
        # Fallback response
        if documents:
            return f"Encontré {len(documents)} vinos relevantes: " + ", ".join([doc.get('metadata', {}).get('name', 'Sin nombre') for doc in documents[:3]])
        else:
            return "No encontré vinos que coincidan con tu búsqueda. ¿Podrías ser más específico?"

# --- Endpoints Mejorados ---

@app.post("/query", response_model=RecommendationResponse)
async def handle_agentic_query_resilient(query: Query = Body(...)):
    """
    ✨ VERSIÓN RESILIENTE: Maneja failures gracefully con connection pooling
    """
    user_prompt = query.prompt
    user_id = query.user_id
    logger.info(f"🧠 Consulta resiliente de {user_id}: \"{user_prompt}\"")

    # 1. Búsqueda resiliente con RAG agéntico
    search_result = await search_wines_with_agentic_rag(user_prompt, user_id)
    wines_found = len(search_result.get('sources', []))
    expanded_queries = search_result.get('expanded_queries', [])
    
    # 2. Generar respuesta (tu lógica existente)
    conversational_response = await generate_agentic_response(user_prompt, search_result, user_id)
    
    # 3. Guardar interacción resiliente
    await save_user_interaction_resilient(user_id, user_prompt, conversational_response, search_result.get('sources', []))
    
    return RecommendationResponse(
        response=conversational_response,
        expanded_queries=expanded_queries,
        wines_found=wines_found
    )

@app.get("/health")
async def health_check_resilient():
    """Health check con información del circuit breaker"""
    try:
        # Verificar servicios con timeout corto usando el cliente simple
        services_status = {"rag_mcp": False, "memory_mcp": False}
        
        try:
            await resilient_client.get_simple(f"{RAG_MCP_URL}/health")
            services_status["rag_mcp"] = True
        except Exception as e:
            logger.warning(f"RAG MCP health check failed: {e}")
        
        try:
            await resilient_client.get_simple(f"{MEMORY_MCP_URL}/health")
            services_status["memory_mcp"] = True
        except Exception as e:
            logger.warning(f"Memory MCP health check failed: {e}")
        
        # Información del circuit breaker
        circuit_info = resilient_client.get_circuit_info()
        
        # Determinar estado general
        all_healthy = services_status["rag_mcp"] and services_status["memory_mcp"]
        status = "healthy" if all_healthy else "degraded"
        
        return {
            "status": status,
            "circuit_breaker": circuit_info,
            "services": {
                **services_status,
                "openai": openai_client is not None
            },
            "config": {
                "rag_url": RAG_MCP_URL,
                "memory_url": MEMORY_MCP_URL,
                "openai_model": OPENAI_MODEL
            }
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "circuit_breaker": resilient_client.get_circuit_info(),
            "services": {
                "rag_mcp": False,
                "memory_mcp": False,
                "openai": openai_client is not None
            }
        }

@app.get("/stats")
async def get_stats_resilient():
    """Estadísticas del sumiller agéntico con información resiliente"""
    try:
        stats = {"rag_stats": {}, "memory_stats": {}, "client_stats": {}}
        
        # Intentar obtener stats de RAG
        try:
            rag_stats = await resilient_client.get_with_retry(f"{RAG_MCP_URL}/stats", max_retries=1)
            stats["rag_stats"] = rag_stats
        except Exception as e:
            stats["rag_stats"] = {"error": str(e)}
        
        # Intentar obtener stats de Memory
        try:
            memory_stats = await resilient_client.get_with_retry(f"{MEMORY_MCP_URL}/stats", max_retries=1)
            stats["memory_stats"] = memory_stats
        except Exception as e:
            stats["memory_stats"] = {"error": str(e)}
        
        # Stats del cliente resiliente
        stats["client_stats"] = {
            "circuit_breaker": resilient_client.get_circuit_info(),
            "pool_initialized": resilient_client.pool._client is not None
        }
        
        return stats
        
    except Exception as e:
        return {"error": f"No se pudieron obtener estadísticas: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)