# sumiller-bot/main.py
"""
Sumiller Bot - Agente de Razonamiento y Conversación con MCP Agentic RAG
Utiliza el nuevo sistema MCP Agentic RAG para búsqueda semántica avanzada y generación contextual.
1. Conecta con el RAG MCP Server para expansión agéntica de consultas.
2. Utiliza memoria conversacional para personalización.
3. Genera respuestas conversacionales mejoradas.
"""
import json
import os
import sys
import logging
import httpx
from openai import AsyncOpenAI
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

# Importar configuración multi-entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# --- Configuración ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del puerto que funciona en local y Cloud Run
PORT = int(os.getenv("PORT", str(config.sumiller_port if config.is_local() else 8080)))

# URLs de los nuevos servicios MCP Agentic RAG
RAG_MCP_URL = config.get_service_url('rag-mcp') if hasattr(config, 'get_service_url') else "http://localhost:8000"
MEMORY_MCP_URL = config.get_service_url('memory-mcp') if hasattr(config, 'get_service_url') else "http://localhost:8002"

OPENAI_API_KEY = config.get_openai_key()

if not OPENAI_API_KEY:
    logger.warning("No se pudo obtener la OpenAI API Key. Las llamadas a OpenAI no funcionarán.")
    openai_client = None
else:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="Sumiller Bot API - Agentic RAG",
    description="Un agente inteligente con RAG agéntico que recomienda vinos personalizados.",
    version="3.0.0"
)

# --- Modelos de Datos ---
class Query(BaseModel):
    prompt: str
    user_id: str = "default_user"  # Para memoria conversacional

class RecommendationResponse(BaseModel):
    response: str
    expanded_queries: List[str] = []
    wines_found: int = 0

# --- Integración con MCP Agentic RAG ---

async def search_wines_with_agentic_rag(user_query: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Utiliza el nuevo sistema MCP Agentic RAG para búsqueda semántica avanzada."""
    async with httpx.AsyncClient() as client:
        try:
            # 1. Primero, obtener contexto de memoria si existe
            memory_context = await get_user_memory(user_id, client)
            
            # 2. Realizar búsqueda con RAG agéntico
            rag_payload = {
                "query": user_query,
                "user_id": user_id,
                "context": memory_context,
                "max_results": 5,
                "expand_query": True  # Habilitar expansión agéntica
            }
            
            response = await client.post(
                f"{RAG_MCP_URL}/query",
                json=rag_payload,
                timeout=15.0
            )
            response.raise_for_status()
            search_result = response.json()
            
            logger.info(f"✅ RAG Agéntico encontró {len(search_result.get('sources', []))} vinos relevantes")
            logger.info(f"📝 Consultas expandidas: {search_result.get('expanded_queries', [])}")
            
            return search_result
            
        except httpx.RequestError as e:
            logger.error(f"Error al conectar con RAG MCP Server: {e}")
            # Fallback: búsqueda simple si RAG falla
            return await simple_search_fallback(user_query, client)
        except httpx.HTTPStatusError as e:
            logger.error(f"RAG MCP Server devolvió un error: {e.response.status_code}")
            return await simple_search_fallback(user_query, client)

async def get_user_memory(user_id: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    """Obtiene el contexto de memoria del usuario."""
    try:
        response = await client.get(
            f"{MEMORY_MCP_URL}/memory/{user_id}",
            timeout=5.0
        )
        if response.status_code == 200:
            memory_data = response.json()
            logger.info(f"💾 Memoria recuperada para usuario {user_id}: {len(memory_data.get('preferences', {}))} preferencias")
            return memory_data
        else:
            return {}
    except Exception as e:
        logger.warning(f"No se pudo recuperar memoria para {user_id}: {e}")
        return {}

async def save_user_interaction(user_id: str, query: str, response: str, wines: List[Dict]) -> None:
    """Guarda la interacción en memoria para futuras personalizaciones."""
    async with httpx.AsyncClient() as client:
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
            
            await client.post(
                f"{MEMORY_MCP_URL}/memory/save",
                json=memory_payload,
                timeout=5.0
            )
            logger.info(f"💾 Interacción guardada en memoria para usuario {user_id}")
        except Exception as e:
            logger.warning(f"No se pudo guardar en memoria: {e}")

async def simple_search_fallback(user_query: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    """Búsqueda simple de fallback si RAG agéntico no está disponible."""
    try:
        # Intentar búsqueda básica en el servicio RAG
        response = await client.post(
            f"{RAG_MCP_URL}/query",
            json={"query": user_query, "max_results": 5},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    # Si todo falla, respuesta vacía
    logger.warning("Fallback: No hay servicios de búsqueda disponibles")
    return {"sources": [], "expanded_queries": [], "error": "Servicios no disponibles"}

# --- Lógica del Agente Inteligente Mejorada ---

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
        
        A) CONSULTAS DE TEORÍA/FORMACIÓN:
        - Explica conceptos de sumillería con fundamentos teóricos
        - Enseña técnicas profesionales
        - Usa terminología especializada
        - Cita principios cuando sea relevante
        
        B) RECOMENDACIONES DE VINOS:
        - Aplica principios de maridaje para justificar recomendaciones
        - Explica POR QUÉ cada vino es adecuado basándote en teoría
        - Menciona características técnicas (acidez, taninos, cuerpo)
        - Incluye temperatura de servicio cuando sea relevante
        
        FORMATO PARA RECOMENDACIONES:
        1. Breve explicación del principio aplicado
        2. Recomendaciones específicas:
           • **Nombre** (Región) - €precio
             [Justificación técnica basada en características del vino]
        
        REGLAS:
        - Máximo 3 vinos recomendados
        - Siempre explica el "por qué" con fundamentos profesionales
        - Usa vocabulario técnico apropiado
        - Menciona temperatura de servicio para vinos recomendados
        - Integra conocimiento teórico en explicaciones prácticas
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
            model="gpt-4-turbo",
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

# --- Endpoint Principal Actualizado ---
@app.post("/query", response_model=RecommendationResponse)
async def handle_agentic_query(query: Query = Body(...)):
    """
    Orquesta el flujo de recomendación usando RAG agéntico avanzado.
    """
    user_prompt = query.prompt
    user_id = query.user_id
    logger.info(f"🧠 Nueva consulta agéntica de {user_id}: \"{user_prompt}\"")

    # 1. Búsqueda con RAG agéntico
    search_result = await search_wines_with_agentic_rag(user_prompt, user_id)
    
    wines_found = len(search_result.get('sources', []))
    expanded_queries = search_result.get('expanded_queries', [])
    
    # 2. Generar respuesta conversacional agéntica
    logger.info("🤖 Generando respuesta con IA agéntica...")
    conversational_response = await generate_agentic_response(user_prompt, search_result, user_id)
    
    # 3. Guardar interacción en memoria para futuras consultas
    await save_user_interaction(user_id, user_prompt, conversational_response, search_result.get('sources', []))
    
    return RecommendationResponse(
        response=conversational_response,
        expanded_queries=expanded_queries,
        wines_found=wines_found
    )

@app.get("/health")
async def health_check():
    """Endpoint de salud del servicio."""
    try:
        # Verificar conectividad con servicios MCP
        async with httpx.AsyncClient() as client:
            rag_health = await client.get(f"{RAG_MCP_URL}/health", timeout=3.0)
            memory_health = await client.get(f"{MEMORY_MCP_URL}/health", timeout=3.0)
            
            return {
                "status": "healthy",
                "services": {
                    "rag_mcp": rag_health.status_code == 200,
                    "memory_mcp": memory_health.status_code == 200,
                    "openai": openai_client is not None
                }
            }
    except Exception as e:
        return {
            "status": "degraded", 
            "error": str(e),
            "services": {
                "rag_mcp": False,
                "memory_mcp": False,
                "openai": openai_client is not None
            }
        }

@app.get("/stats")
async def get_stats():
    """Estadísticas del sumiller agéntico."""
    try:
        async with httpx.AsyncClient() as client:
            rag_stats = await client.get(f"{RAG_MCP_URL}/stats", timeout=5.0)
            memory_stats = await client.get(f"{MEMORY_MCP_URL}/stats", timeout=5.0)
            
            return {
                "rag_stats": rag_stats.json() if rag_stats.status_code == 200 else {},
                "memory_stats": memory_stats.json() if memory_stats.status_code == 200 else {}
            }
    except Exception as e:
        return {"error": f"No se pudieron obtener estadísticas: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)