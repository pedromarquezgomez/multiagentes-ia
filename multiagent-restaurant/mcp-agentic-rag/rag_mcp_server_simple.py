#!/usr/bin/env python3
"""
Servidor RAG MCP Simplificado para resolver latencia
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import openai
from sentence_transformers import SentenceTransformer

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración global
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY"))
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
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

class SimpleRAGEngine:
    """Motor de RAG simplificado"""
    
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
        """Inicializar conexiones a ChromaDB"""
        try:
            logger.info(f"Conectando a ChromaDB en {CHROMA_HOST}:{CHROMA_PORT}")
            self.vector_db = chromadb.HttpClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
            
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
                
            logger.info("ChromaDB inicializada exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando ChromaDB: {e}")
            raise
    
    def _embed_text(self, text: str) -> List[float]:
        """Generar embeddings para texto"""
        return self.embedding_model.encode(text).tolist()
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None, doc_id: str = None) -> str:
        """Agregar documento a la base de conocimiento"""
        try:
            if not doc_id:
                doc_id = f"doc_{len(self.collection.get()['ids']) + 1}"
            
            embedding = self._embed_text(content)
            
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

# Instancia global del motor RAG
rag_engine = SimpleRAGEngine()

# Aplicación FastAPI
app = FastAPI(title="Simple RAG Server", version="1.0.0")

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
    return {"status": "healthy", "message": "Server is running"}

@app.post("/query")
async def query_endpoint(query_data: QueryRequest):
    """Endpoint principal para consultas RAG"""
    start_total = time.time()
    logger.info(f"=== NUEVA CONSULTA: {query_data.query} ===")

    try:
        # Asegurar que rag_engine esté inicializado
        if rag_engine.collection is None:
            logger.info("Inicializando rag_engine...")
            await rag_engine.initialize()

        # Paso 1: Obtener embeddings de la consulta
        start_embedding = time.time()
        query_embedding = rag_engine._embed_text(query_data.query)
        end_embedding = time.time()
        embedding_time = end_embedding - start_embedding
        logger.info(f"⏱️  EMBEDDING: {embedding_time:.4f}s")

        # Paso 2: Buscar documentos relevantes en ChromaDB
        start_chroma_search = time.time()
        results = rag_engine.collection.query(
            query_embeddings=[query_embedding],
            n_results=query_data.max_results,
            include=['documents', 'metadatas', 'distances']
        )
        end_chroma_search = time.time()
        chroma_time = end_chroma_search - start_chroma_search
        logger.info(f"⏱️  CHROMADB: {chroma_time:.4f}s")

        # Procesar resultados
        documents = results['documents'][0] if results and 'documents' in results else []
        metadatas = results['metadatas'][0] if results and 'metadatas' in results else []
        distances = results['distances'][0] if results and 'distances' in results else []

        logger.info(f"📄 Documentos encontrados: {len(documents)}")

        # Construir fuentes
        sources = []
        context_str = ""
        for i, (doc_content, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            source_entry = {
                "content": doc_content,
                "metadata": metadata,
                "relevance_score": 1 - distance,
                "rank": i + 1
            }
            sources.append(source_entry)
            context_str += f"Fuente {i+1}:\n{doc_content}\n\n"

        # Paso 3: Generar respuesta usando DeepSeek
        start_deepseek_call = time.time()
        
        if rag_engine.deepseek_client and context_str.strip():
            logger.info("🤖 Llamando a DeepSeek...")
            
            messages = [
                {"role": "system", "content": "Eres un asistente sumiller experto. Usa el contexto proporcionado para responder a las preguntas sobre vinos. Si no puedes encontrar la respuesta en el contexto, indica que no tienes esa información. No alucines."},
                {"role": "user", "content": f"Contexto:\n{context_str}\n\nPregunta: {query_data.query}"}
            ]
            
            response = rag_engine.deepseek_client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stream=False
            )
            
            llm_answer = response.choices[0].message.content if response.choices else "No se pudo obtener una respuesta del modelo."
        elif not context_str.strip():
            llm_answer = f"No encontré información relevante en la base de conocimiento para la consulta: '{query_data.query}'"
        else:
            llm_answer = f"Basado en {len(sources)} fuentes encontradas para: '{query_data.query}' (DeepSeek no disponible)"
        
        end_deepseek_call = time.time()
        deepseek_time = end_deepseek_call - start_deepseek_call
        logger.info(f"⏱️  DEEPSEEK: {deepseek_time:.4f}s")

        end_total = time.time()
        total_time = end_total - start_total
        
        logger.info(f"⏱️  TOTAL: {total_time:.4f}s")
        logger.info("=== FIN CONSULTA ===")

        return {
            "answer": llm_answer,
            "sources": sources,
            "context_used": {"query": query_data.query, "context": context_str},
            "timing": {
                "embedding": f"{embedding_time:.4f}s",
                "chromadb_search": f"{chroma_time:.4f}s",
                "deepseek_call": f"{deepseek_time:.4f}s",
                "total": f"{total_time:.4f}s"
            }
        }

    except Exception as e:
        end_total = time.time()
        total_time = end_total - start_total
        logger.error(f"❌ ERROR en /query después de {total_time:.4f}s: {e}")
        return {
            "answer": f"Error procesando consulta: {str(e)}",
            "sources": [],
            "context_used": {"query": query_data.query, "error": str(e)},
            "timing": {"total": f"{total_time:.4f}s", "error": True}
        }

@app.post("/documents")
async def add_document_endpoint(request: DocumentRequest):
    """Endpoint para agregar documentos"""
    try:
        doc_id = await rag_engine.add_document(
            request.content,
            request.metadata,
            request.doc_id
        )
        return {"doc_id": doc_id, "status": "added"}
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 