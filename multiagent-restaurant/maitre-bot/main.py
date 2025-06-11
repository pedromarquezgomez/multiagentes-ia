# maitre-bot/main.py
"""
Maitre Bot - Agente orquestador que recibe consultas y las redirige al sumiller
Preparado para despliegue en Google Cloud Run
"""
import json
import httpx
import time
import sys
import os
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

# Importar configuración multi-entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Importar módulo de autenticación Firebase
from firebase_auth import initialize_firebase, verify_firebase_token, get_user_info

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Cliente HTTP reutilizable
http_client = httpx.AsyncClient()

# Esquema de seguridad
token_auth_scheme = HTTPBearer()

# CORS para permitir llamadas desde la UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del servicio
SUMILLER_URL = config.get_service_url('sumiller')
# Configuración del puerto que funciona en local y Cloud Run
PORT = int(os.environ.get("PORT", str(config.maitre_port if config.is_local() else 8080)))

logger.info(f"🚀 Iniciando Maitre Bot en puerto {PORT}")
logger.info(f"🎯 URL del Sumiller: {SUMILLER_URL}")

# Inicializar Firebase
firebase_initialized = initialize_firebase()
if firebase_initialized:
    logger.info("🔥 Firebase configurado correctamente")
else:
    logger.warning("⚠️ Firebase no pudo inicializarse, funcionando en modo desarrollo")

# Modelos de datos
class MCPMessage(BaseModel):
    system: str
    user: str
    context: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = {}

class QueryResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = {}

# Función para verificar autenticación (mejorada)
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    """
    Verifica el token de autenticación Firebase usando el esquema de seguridad de FastAPI.
    """
    # En modo desarrollo (sin Firebase), permitir acceso
    if not firebase_initialized:
        logger.warning("🔓 Modo desarrollo: permitiendo acceso sin autenticación")
        return {"uid": "dev-user", "email": "dev@example.com", "verified": True}
    
    try:
        user_info = verify_firebase_token(token.credentials)
        if not user_info.get("verified"):
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        return user_info
    except Exception as e:
        logger.error(f"❌ Error verificando autenticación: {e}")
        # En modo desarrollo, si hay error de Firebase, permitir acceso de todas formas
        logger.warning("🔓 Modo desarrollo: permitiendo acceso por error de Firebase")
        return {"uid": "dev-user", "email": "dev@example.com", "verified": True}

@app.get("/")
async def health_check():
    """Health check endpoint para Google Cloud Run"""
    logger.info("🔍 Health check solicitado")
    return {
        "status": "healthy", 
        "service": "maitre-bot",
        "firebase": firebase_initialized
    }

@app.post("/query")
async def handle_query(
    request: QueryRequest, 
    current_user: dict = Depends(get_current_user)
) -> QueryResponse:
    """
    Endpoint principal que recibe consultas del cliente y las redirige al sumiller.
    """
    return await _handle_query_internal(request, current_user)

@app.post("/query-dev")
async def handle_query_dev(request: QueryRequest) -> QueryResponse:
    """
    Endpoint de desarrollo sin autenticación para testing local.
    """
    dev_user = {"uid": "dev-user", "email": "dev@example.com", "verified": True}
    return await _handle_query_internal(request, dev_user)

async def _handle_query_internal(request: QueryRequest, current_user: dict) -> QueryResponse:
    """
    Lógica interna para manejar consultas (usado tanto por endpoint autenticado como dev).
    """
    try:
        logger.info(f"📥 Consulta recibida de {current_user.get('email')}: {request.prompt}")
        
        # El cuerpo de la solicitud ahora es directamente compatible con el nuevo sumiller.
        # Simplemente pasamos el diccionario de la solicitud original.
        request_body = request.dict()
        logger.info(f"📤 Enviando consulta al sumiller: {request_body}")
        
        logger.info(f"🔗 Conectando con sumiller en: {SUMILLER_URL}/query")
        response = await http_client.post(
            f"{SUMILLER_URL}/query",
            json=request_body,
            timeout=60.0  # Aumentado a 60s por las llamadas a LLM
        )
            
        logger.info(f"📥 Respuesta del sumiller - Status: {response.status_code}")
            
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"❌ Error del sumiller ({response.status_code}): {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Error comunicando con sumiller: {response.status_code} - {error_detail}"
            )
        
        # Obtenemos la respuesta directa del sumiller
        sumiller_response_data = response.json()
        logger.info(f"✅ Respuesta del sumiller: {sumiller_response_data}")

        # La respuesta del sumiller puede ser un string o un JSON.
        # Si es un JSON con una clave 'response', la usamos. Si no, usamos el texto completo.
        final_response = sumiller_response_data.get('response', str(sumiller_response_data))
        
        logger.info(f"📤 Enviando respuesta directa del sumiller al usuario {current_user.get('email')}")
        return QueryResponse(
            response=final_response,
            metadata={
                "source": "sumiller-bot",
                "user_id": current_user.get('uid')
            }
        )
            
    except httpx.RequestError as e:
        logger.error(f"❌ Error de comunicación con sumiller: {e}")
        raise HTTPException(status_code=503, detail="Servicio sumiller no disponible")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Endpoint para obtener información del usuario actual
    """
    logger.info(f"👤 Solicitud de perfil para usuario: {current_user.get('email')}")
    return current_user

@app.post("/a2a/message")
async def receive_a2a_message(message: MCPMessage):
    """
    Endpoint para recibir mensajes A2A de otros agentes
    (Por ahora solo logging, se puede extender)
    """
    logger.info(f"📨 Mensaje A2A recibido: {message.dict()}")
    return {"status": "received", "message_id": f"maitre-{int(time.time()*1000)}"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor Uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# Para desplegar en Google Cloud Run:
# gcloud run deploy maitre-bot \
#   --source . \
#   --region us-central1 \
#   --allow-unauthenticated \
#   --set-env-vars SUMILLER_URL=https://sumiller-bot-xxxxx-uc.a.run.app