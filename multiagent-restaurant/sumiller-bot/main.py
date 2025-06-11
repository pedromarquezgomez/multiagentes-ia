# sumiller-bot/main.py
"""
Sumiller Bot - Agente de Razonamiento y Conversación
Utiliza ChromaDB (via mcp-server) para búsqueda semántica inteligente y OpenAI para respuestas conversacionales.
1. Envía la consulta del usuario al mcp-server para búsqueda vectorial.
2. Genera una respuesta conversacional basada en los vinos relevantes encontrados.
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

PORT = int(os.getenv("PORT", str(config.sumiller_port if config.is_local() else 8001)))
MCP_SERVER_URL = config.get_service_url('mcp')

OPENAI_API_KEY = config.get_openai_key()

if not OPENAI_API_KEY:
    logger.warning("No se pudo obtener la OpenAI API Key. Las llamadas a OpenAI no funcionarán.")
    openai_client = None
else:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="Sumiller Bot API",
    description="Un agente inteligente que recomienda vinos de un catálogo.",
    version="2.0.0"
)

# --- Modelos de Datos ---
class Query(BaseModel):
    prompt: str

class RecommendationResponse(BaseModel):
    response: str

# --- Lógica de Obtención de Datos ---
async def search_wines_from_catalog(user_query: str) -> List[Dict[str, Any]]:
    """Utiliza el mcp-server para hacer búsqueda semántica inteligente."""
    async with httpx.AsyncClient() as client:
        try:
            # Usar el nuevo endpoint de búsqueda semántica
            response = await client.post(
                f"{MCP_SERVER_URL}/search",
                json={"query": user_query, "limit": 5},
                timeout=10.0
            )
            response.raise_for_status()
            search_result = response.json()
            
            # Extraer la lista de vinos del resultado
            wines = search_result.get("wines", [])
            logger.info(f"✅ Búsqueda semántica encontró {len(wines)} vinos relevantes")
            
            return wines
            
        except httpx.RequestError as e:
            logger.error(f"Error al conectar con mcp-server: {e}")
            raise HTTPException(status_code=503, detail="No se pudo comunicar con el catálogo de vinos.")
        except httpx.HTTPStatusError as e:
            logger.error(f"mcp-server devolvió un error: {e.response.status_code}")
            raise HTTPException(status_code=e.response.status_code, detail="El catálogo de vinos devolvió un error.")

# --- Lógica del Agente Inteligente (Simplificada) ---

async def generate_conversational_response(user_query: str, filtered_wines: List[Dict[str, Any]]) -> str:
    """
    Genera una respuesta conversacional basada en los vinos pre-filtrados por ChromaDB.
    """
    if not openai_client:
        return "La API de OpenAI no está configurada, pero estos son los vinos que encontré: " + json.dumps(filtered_wines)

    if not filtered_wines:
        system_prompt = """
        Eres un sumiller experto llamado Sumy, eres amable, cercano y empático.
        Tu tarea es informar al usuario que no has podido encontrar un vino que coincida con su búsqueda en tu catálogo actual.
        - Discúlpate amablemente.
        - Explica que has buscado cuidadosamente pero no tienes la combinación perfecta para su petición.
        - Invítale a que intente con otra descripción o tipo de vino. Sé proactivo, quizás puedas sugerirle que pida "un tinto con cuerpo" o "un blanco afrutado" para guiarle.
        - Tu tono debe ser servicial y nunca negativo.
        """
        user_content = f"Mi consulta fue: \"{user_query}\""
    else:
        system_prompt = """
        Eres Sumy, un sumiller experto. Responde de forma concisa y precisa.
        
        REGLAS ESTRICTAS:
        - Usa ÚNICAMENTE los vinos de la lista JSON proporcionada
        - NO inventes nombres, precios, descripciones o características
        - Respuesta máxima: 3-4 líneas por vino
        - Menciona EXACTAMENTE: nombre, precio, región, por qué es ideal
        - Si hay varios vinos, recomienda máximo 2-3
        - Sé directo y útil, sin texto decorativo excesivo
        
        FORMATO:
        • **Nombre del Vino** (Región) - €precio
          Perfecto para [motivo específico basado en pairing/descripción]
        """
        user_content = f"Mi consulta original fue: \"{user_query}\"\n\nEstos son los vinos que mi sistema de búsqueda inteligente encontró como más relevantes:\n{json.dumps(filtered_wines, indent=2, ensure_ascii=False)}"
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error al generar respuesta conversacional con OpenAI: {e}")
        raise HTTPException(status_code=500, detail="Tuve problemas para generar una respuesta creativa.")

# --- Endpoint Principal ---
@app.post("/query", response_model=RecommendationResponse)
async def handle_query(query: Query = Body(...)):
    """
    Orquesta el flujo de recomendación de vinos usando búsqueda vectorial.
    """
    user_prompt = query.prompt
    logger.info(f"Recibida nueva consulta: \"{user_prompt}\"")

    # 1. Búsqueda semántica inteligente via mcp-server
    relevant_wines = await search_wines_from_catalog(user_prompt)
    if not relevant_wines:
        logger.info("No se encontraron vinos relevantes, generando respuesta de disculpa")
    
    # 2. Generar respuesta conversacional
    logger.info("Generando respuesta conversacional final...")
    conversational_response = await generate_conversational_response(user_prompt, relevant_wines)
    
    return RecommendationResponse(response=conversational_response)

@app.get("/health")
async def health_check():
    """Endpoint de salud del servicio."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)