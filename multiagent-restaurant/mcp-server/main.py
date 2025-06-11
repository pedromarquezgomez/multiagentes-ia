# mcp-server/main.py
"""
Servidor del Catálogo de Vinos con ChromaDB - Búsqueda vectorial inteligente
"""
import json
import os
import sys
import logging
import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Importar configuración multi-entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# --- Configuración ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del puerto que funciona en local y Cloud Run
PORT = int(os.getenv("PORT", str(config.mcp_port if config.is_local() else 8080)))

# Variables globales para ChromaDB
wine_collection = None
wine_catalog_raw = []

app = FastAPI(
    title="Servidor del Catálogo de Vinos con ChromaDB",
    description="Un microservicio inteligente para búsqueda vectorial de vinos.",
    version="2.0.0"
)

# --- Modelos de Datos (Pydantic) ---
class Wine(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    region: str
    vintage: int
    description: str
    pairing: str
    price: float
    rating: int
    stock: int

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 5

class SearchResponse(BaseModel):
    wines: List[Dict[str, Any]]
    total_found: int

# --- Inicialización de ChromaDB ---
def initialize_wine_database():
    """Inicializa ChromaDB y carga los vinos desde wines.json"""
    global wine_collection, wine_catalog_raw
    
    logger.info("🍷 Iniciando base de datos vectorial de vinos...")
    
    try:
        # Cargar datos desde wines.json
        with open("wines.json", "r", encoding="utf-8") as f:
            wine_data = json.load(f)
            
        # Asignar IDs únicos
        for i, wine_dict in enumerate(wine_data):
            wine_dict["id"] = i + 1
            
        wine_catalog_raw = [Wine(**w).dict() for w in wine_data]
        logger.info(f"✅ {len(wine_catalog_raw)} vinos cargados desde JSON.")
        
        # Inicializar ChromaDB
        client = chromadb.Client()
        
        # Intentar crear o obtener la colección
        try:
            wine_collection = client.create_collection(
                name="wine_catalog",
                metadata={"description": "Catálogo de vinos con búsqueda semántica"}
            )
            logger.info("📦 Colección de ChromaDB creada.")
        except Exception:
            wine_collection = client.get_collection(name="wine_catalog")
            logger.info("📦 Colección de ChromaDB existente recuperada.")
        
        # Verificar si ya hay datos en la colección
        existing_count = wine_collection.count()
        if existing_count == 0:
            logger.info("💾 Cargando vinos en ChromaDB...")
            
            # Preparar documentos para embeddings
            documents = []
            metadatas = []
            ids = []
            
            for wine in wine_catalog_raw:
                # Crear un documento rico para embeddings
                doc_text = f"""
                {wine['name']} - {wine['type']} de {wine['region']}
                Añada: {wine['vintage']}
                Descripción: {wine['description']}
                Maridaje: {wine['pairing']}
                Precio: €{wine['price']}
                Puntuación: {wine['rating']}/100
                """.strip()
                
                documents.append(doc_text)
                metadatas.append(wine)
                ids.append(str(wine['id']))
            
            # Añadir a ChromaDB en batch
            wine_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ {len(documents)} vinos indexados en ChromaDB.")
        else:
            logger.info(f"📚 ChromaDB ya contiene {existing_count} vinos.")
            
    except FileNotFoundError:
        logger.error("❌ Archivo 'wines.json' no encontrado.")
        return False
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        return False
    
    return True

# --- Funciones de Búsqueda ---
def search_wines_semantic(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Realiza búsqueda semántica en el catálogo de vinos"""
    if not wine_collection:
        return []
    
    try:
        # Detectar tipo de vino para filtrado inteligente
        wine_types = {
            "tinto": ["tinto", "rojo", "red", "negro", "tempranillo", "garnacha", "mencia"],
            "blanco": ["blanco", "white", "claro", "verdejo", "albariño", "godello"],
            "espumoso": ["espumoso", "cava", "champagne", "burbujas", "sparkling"],
            "rosado": ["rosado", "rosé", "clarete"]
        }
        
        detected_type = None
        query_lower = query.lower()
        
        # Buscar tipo de vino en la consulta
        for wine_type, keywords in wine_types.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_type = wine_type.capitalize()
                break
        
        # Realizar búsqueda con o sin filtro
        if detected_type:
            logger.info(f"🔍 Búsqueda filtrada por tipo: {detected_type}")
            results = wine_collection.query(
                query_texts=[query],
                n_results=limit,
                where={"type": detected_type}
            )
            
            # Si no hay resultados con filtro, buscar sin filtro
            if not results["metadatas"] or not results["metadatas"][0]:
                logger.info("🔍 Sin resultados con filtro, buscando sin restricción...")
                results = wine_collection.query(
                    query_texts=[query],
                    n_results=limit
                )
        else:
            logger.info("🔍 Búsqueda semántica general")
            results = wine_collection.query(
                query_texts=[query],
                n_results=limit
            )
        
        # Extraer y limpiar resultados
        if results["metadatas"] and results["metadatas"][0]:
            wines = results["metadatas"][0]
            logger.info(f"✅ {len(wines)} vinos encontrados")
            return wines
        else:
            logger.info("ℹ️ No se encontraron vinos")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error en búsqueda semántica: {e}")
        return []

# --- Endpoints de la API ---
@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    wine_count = wine_collection.count() if wine_collection else 0
    return {
        "status": "healthy", 
        "wines_loaded": len(wine_catalog_raw),
        "wines_indexed": wine_count,
        "chromadb_active": wine_collection is not None
    }

@app.get("/wines", response_model=List[Wine])
async def get_all_wines():
    """Devuelve la lista completa de vinos (para compatibilidad)"""
    if not wine_catalog_raw:
        raise HTTPException(
            status_code=404, 
            detail="Catálogo de vinos no disponible"
        )
    return wine_catalog_raw

@app.post("/search", response_model=SearchResponse)
async def search_wines(search_query: SearchQuery):
    """Búsqueda semántica inteligente de vinos"""
    if not wine_collection:
        raise HTTPException(
            status_code=503,
            detail="Base de datos vectorial no disponible"
        )
    
    wines = search_wines_semantic(search_query.query, search_query.limit)
    
    return SearchResponse(
        wines=wines,
        total_found=len(wines)
    )

@app.get("/search/{query}")
async def search_wines_get(query: str, limit: int = 5):
    """Búsqueda semántica via GET (para facilidad de uso)"""
    if not wine_collection:
        raise HTTPException(
            status_code=503,
            detail="Base de datos vectorial no disponible"
        )
    
    wines = search_wines_semantic(query, limit)
    
    return {
        "query": query,
        "wines": wines,
        "total_found": len(wines)
    }

# --- Inicialización al arrancar ---
@app.on_event("startup")
async def startup_event():
    """Inicializar base de datos al arrancar"""
    success = initialize_wine_database()
    if not success:
        logger.error("❌ Fallo crítico en la inicialización")

# --- Ejecución del Servidor ---
if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Iniciando servidor en el puerto {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)