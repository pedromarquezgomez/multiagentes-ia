#!/usr/bin/env python3
"""
Servidor RAG MCP Agéntico
Implementa un sistema completo de RAG con capacidades agénticas usando MCP
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# MCP SDK imports
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Vector DB imports
import chromadb
from chromadb.config import Settings
import openai
from sentence_transformers import SentenceTransformer

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración global
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY"))  # Fallback a OpenAI key si DeepSeek no está disponible
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))

# Modelos de datos
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    max_results: int = 5

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    doc_id: Optional[str] = None

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: Dict[str, Any]

class AgenticRAGEngine:
    """Motor de RAG Agéntico con capacidades avanzadas"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_db = None
        self.collection = None
        self.deepseek_client = None
        
        if DEEPSEEK_API_KEY:
            self.deepseek_client = openai.OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL
            )
    
    async def initialize(self):
        """Inicializar conexiones a bases de datos vectoriales"""
        max_retries = 5
        retry_delay = 5  # segundos
        
        for attempt in range(max_retries):
            try:
                if VECTOR_DB_TYPE == "chroma":
                    logger.info(f"Intentando conectar a ChromaDB en {CHROMA_HOST}:{CHROMA_PORT} (intento {attempt + 1}/{max_retries})")
                    self.vector_db = chromadb.HttpClient(
                        host=CHROMA_HOST,
                        port=CHROMA_PORT,
                        settings=Settings(
                            allow_reset=True,
                            anonymized_telemetry=False
                        )
                    )
                    # Crear o obtener colección
                    try:
                        self.collection = self.vector_db.get_collection("rag_documents")
                        logger.info("Colección 'rag_documents' recuperada exitosamente")
                    except Exception as e:
                        logger.info(f"Creando nueva colección 'rag_documents': {e}")
                        self.collection = self.vector_db.create_collection(
                            "rag_documents",
                            metadata={"hnsw:space": "cosine"}
                        )
                        logger.info("Colección 'rag_documents' creada exitosamente")
                
                logger.info(f"Vector DB inicializada exitosamente: {VECTOR_DB_TYPE}")
                return
                
            except Exception as e:
                logger.error(f"Error inicializando vector DB (intento {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Reintentando en {retry_delay} segundos...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise Exception(f"No se pudo conectar a ChromaDB después de {max_retries} intentos")
    
    def _embed_text(self, text: str) -> List[float]:
        """Generar embeddings para texto"""
        return self.embedding_model.encode(text).tolist()
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None, doc_id: str = None) -> str:
        """Agregar documento a la base de conocimiento"""
        try:
            if not doc_id:
                doc_id = f"doc_{len(self.collection.get()['ids']) + 1}"
            
            embedding = self._embed_text(content)
            
            # Agregar a ChromaDB
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            logger.info(f"Documento agregado: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error agregando documento: {e}")
            raise
    
    async def semantic_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Búsqueda semántica en la base de conocimiento"""
        try:
            query_embedding = self._embed_text(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'relevance_score': 1 - distance,  # Convertir distancia a score
                        'rank': i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    async def agentic_query_expansion(self, query: str, context: Dict[str, Any] = None) -> List[str]:
        """Expansión agéntica de consultas usando LLM"""
        if not self.deepseek_client:
            return [query]  # Fallback si no hay DeepSeek
        
        try:
            system_prompt = """Eres un experto en expandir consultas para mejorar la recuperación de información.
            Dado una consulta del usuario, genera variaciones y reformulaciones que puedan ayudar a encontrar información relevante.
            Incluye sinónimos, términos relacionados y diferentes formas de expresar la misma pregunta.
            
            Responde con un JSON que contenga una lista de consultas expandidas."""
            
            user_prompt = f"""
            Consulta original: "{query}"
            Contexto adicional: {json.dumps(context or {}, indent=2)}
            
            Genera 3-5 variaciones de esta consulta para mejorar la búsqueda.
            """
            
            response = self.deepseek_client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            
            # Intentar parsear JSON
            try:
                expanded_queries = json.loads(result)
                if isinstance(expanded_queries, list):
                    return [query] + expanded_queries[:4]  # Original + 4 expansiones max
                elif isinstance(expanded_queries, dict) and 'queries' in expanded_queries:
                    return [query] + expanded_queries['queries'][:4]
            except:
                # Si falla el parsing, usar la consulta original
                pass
            
            return [query]
            
        except Exception as e:
            logger.error(f"Error en expansión de consulta: {e}")
            return [query]
    
    async def generate_answer(self, query: str, sources: List[Dict[str, Any]], context: Dict[str, Any] = None) -> str:
        """Generar respuesta usando LLM con fuentes recuperadas"""
        if not self.deepseek_client:
            # Fallback sin LLM
            return f"Basado en {len(sources)} fuentes encontradas para: '{query}'"
        
        try:
            # Construir contexto de fuentes
            sources_text = "\n\n".join([
                f"Fuente {i+1} (relevancia: {source.get('relevance_score', 0):.2f}):\n{source['content']}"
                for i, source in enumerate(sources[:3])  # Máximo 3 fuentes
            ])
            
            system_prompt = """Eres un asistente inteligente que responde preguntas basándose en fuentes proporcionadas.
            Usa SOLAMENTE la información de las fuentes para responder. Si la información no está en las fuentes, dilo claramente.
            Cita las fuentes relevantes en tu respuesta."""
            
            user_prompt = f"""
            Pregunta: {query}
            
            Contexto adicional: {json.dumps(context or {}, indent=2)}
            
            Fuentes disponibles:
            {sources_text}
            
            Responde la pregunta basándote únicamente en las fuentes proporcionadas.
            """
            
            response = self.deepseek_client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return f"Error generando respuesta basada en {len(sources)} fuentes para: '{query}'"
    
    async def agentic_rag_query(self, query: str, context: Dict[str, Any] = None, max_results: int = 5) -> RAGResponse:
        """Consulta RAG agéntica completa"""
        try:
            # 1. Expansión agéntica de consulta
            expanded_queries = await self.agentic_query_expansion(query, context)
            logger.info(f"Consultas expandidas: {expanded_queries}")
            
            # 2. Búsqueda semántica multi-consulta
            all_sources = []
            for exp_query in expanded_queries:
                sources = await self.semantic_search(exp_query, max_results=3)
                all_sources.extend(sources)
            
            # 3. Deduplicación y ranking
            seen_content = set()
            unique_sources = []
            for source in all_sources:
                content_hash = hash(source['content'][:100])  # Hash de los primeros 100 chars
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_sources.append(source)
            
            # Ordenar por relevancia
            unique_sources.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            top_sources = unique_sources[:max_results]
            
            # 4. Generación de respuesta
            answer = await self.generate_answer(query, top_sources, context)
            
            return RAGResponse(
                answer=answer,
                sources=top_sources,
                context_used=context or {}
            )
            
        except Exception as e:
            logger.error(f"Error en consulta RAG agéntica: {e}")
            return RAGResponse(
                answer=f"Error procesando consulta: {str(e)}",
                sources=[],
                context_used=context or {}
            )

# Instancia global del motor RAG
rag_engine = AgenticRAGEngine()

# Servidor MCP
mcp_server = Server("agentic-rag-server")

@mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    """Listar herramientas disponibles"""
    return [
        types.Tool(
            name="search_knowledge",
            description="Buscar información en la base de conocimiento usando RAG agéntico",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta o pregunta a buscar"
                    },
                    "context": {
                        "type": "object",
                        "description": "Contexto adicional para la búsqueda"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Número máximo de resultados",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="add_document",
            description="Agregar un nuevo documento a la base de conocimiento",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Contenido del documento"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadatos del documento"
                    },
                    "doc_id": {
                        "type": "string",
                        "description": "ID opcional del documento"
                    }
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="get_collection_stats",
            description="Obtener estadísticas de la colección de documentos",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Ejecutar herramienta solicitada"""
    try:
        if name == "search_knowledge":
            query = arguments.get("query", "")
            context = arguments.get("context", {})
            max_results = arguments.get("max_results", 5)
            
            result = await rag_engine.agentic_rag_query(query, context, max_results)
            
            response = {
                "answer": result.answer,
                "sources": result.sources,
                "context_used": result.context_used,
                "num_sources": len(result.sources)
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(response, indent=2, ensure_ascii=False)
            )]
            
        elif name == "add_document":
            content = arguments.get("content", "")
            metadata = arguments.get("metadata", {})
            doc_id = arguments.get("doc_id")
            
            result_id = await rag_engine.add_document(content, metadata, doc_id)
            
            return [types.TextContent(
                type="text",
                text=f"Documento agregado exitosamente con ID: {result_id}"
            )]
            
        elif name == "get_collection_stats":
            if rag_engine.collection:
                stats = rag_engine.collection.get()
                num_docs = len(stats['ids'])
                
                response = {
                    "total_documents": num_docs,
                    "collection_name": "rag_documents",
                    "vector_db_type": VECTOR_DB_TYPE
                }
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="Colección no inicializada"
                )]
        else:
            raise ValueError(f"Herramienta desconocida: {name}")
            
    except Exception as e:
        logger.error(f"Error ejecutando herramienta {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

@mcp_server.list_resources()
async def list_resources() -> List[types.Resource]:
    """Listar recursos disponibles"""
    return [
        types.Resource(
            uri="knowledge://stats",
            name="Knowledge Base Statistics",
            description="Estadísticas de la base de conocimiento",
            mimeType="application/json"
        ),
        types.Resource(
            uri="knowledge://documents",
            name="Documents Collection",
            description="Colección completa de documentos",
            mimeType="application/json"
        )
    ]

@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Leer recurso solicitado"""
    if uri == "knowledge://stats":
        if rag_engine.collection:
            stats = rag_engine.collection.get()
            response = {
                "total_documents": len(stats['ids']),
                "collection_name": "rag_documents",
                "vector_db_type": VECTOR_DB_TYPE,
                "embedding_model": "all-MiniLM-L6-v2"
            }
            return json.dumps(response, indent=2)
        else:
            return json.dumps({"error": "Colección no inicializada"})
            
    elif uri == "knowledge://documents":
        if rag_engine.collection:
            docs = rag_engine.collection.get()
            response = {
                "documents": [
                    {
                        "id": doc_id,
                        "content": content[:200] + "..." if len(content) > 200 else content,
                        "metadata": metadata
                    }
                    for doc_id, content, metadata in zip(
                        docs['ids'],
                        docs['documents'],
                        docs['metadatas']
                    )
                ]
            }
            return json.dumps(response, indent=2, ensure_ascii=False)
        else:
            return json.dumps({"error": "Colección no inicializada"})
    else:
        raise ValueError(f"Recurso desconocido: {uri}")

# FastAPI para HTTP (opcional)
app = FastAPI(title="Agentic RAG MCP Server", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Inicializar al arrancar"""
    await rag_engine.initialize()
    
    # Cargar documentos de ejemplo si existen
    knowledge_dir = Path("/app/knowledge_base")
    if knowledge_dir.exists():
        for file_path in knowledge_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    metadata = {"source": file_path.name, "type": "text"}
                    await rag_engine.add_document(content, metadata, file_path.stem)
                logger.info(f"Documento cargado: {file_path.name}")
            except Exception as e:
                logger.error(f"Error cargando {file_path}: {e}")

@app.get("/health")
async def health_check():
    """Verificación de salud"""
    return {"status": "healthy", "vector_db": VECTOR_DB_TYPE}

@app.post("/query", response_model=RAGResponse)
async def query_endpoint(request: QueryRequest):
    """Endpoint HTTP para consultas RAG"""
    return await rag_engine.agentic_rag_query(
        request.query,
        request.context,
        request.max_results
    )

@app.post("/documents")
async def add_document_endpoint(request: DocumentRequest):
    """Endpoint HTTP para agregar documentos"""
    doc_id = await rag_engine.add_document(
        request.content,
        request.metadata,
        request.doc_id
    )
    return {"doc_id": doc_id, "status": "added"}

async def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        # Modo HTTP
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Modo MCP stdio
        await rag_engine.initialize()
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )

if __name__ == "__main__":
    asyncio.run(main())