#!/usr/bin/env python3
"""
Servidor RAG MCP Simple - SIN base de datos vectorial
Usa TF-IDF + OpenAI para búsqueda y respuestas
"""

import os
import json
import asyncio
import logging
import time
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

# Búsqueda simple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import openai

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración global
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
    """Motor de RAG Simple sin base de datos vectorial"""
    
    def __init__(self):
        self.documents = []  # Lista de documentos en memoria
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.doc_vectors = None
        self.openai_client = None
        
        if OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL
            )
    
    async def initialize(self):
        """Inicializar con documentos de conocimiento base"""
        try:
            knowledge_base_path = Path("knowledge_base")
            if knowledge_base_path.exists():
                logger.info("Cargando documentos de knowledge_base")
                await self._load_knowledge_base(knowledge_base_path)
            else:
                logger.info("No se encontró knowledge_base, iniciando con documentos vacíos")
                # Crear algunos documentos de ejemplo sobre vinos
                await self._create_sample_documents()
            
            logger.info(f"RAG Engine inicializado con {len(self.documents)} documentos")
            
        except Exception as e:
            logger.error(f"Error inicializando RAG Engine: {e}")
            await self._create_sample_documents()
    
    async def _load_knowledge_base(self, kb_path: Path):
        """Cargar documentos desde archivos"""
        for file_path in kb_path.rglob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = {
                    "content": content,
                    "metadata": {
                        "source": str(file_path),
                        "filename": file_path.name
                    },
                    "doc_id": str(file_path)
                }
                self.documents.append(doc)
                
            except Exception as e:
                logger.warning(f"Error cargando {file_path}: {e}")
        
        await self._build_index()
    
    async def _create_sample_documents(self):
        """Crear documentos de ejemplo sobre vinos"""
        sample_docs = [
            {
                "content": "Los vinos tintos españoles son conocidos por su calidad excepcional. Rioja y Ribera del Duero son dos de las denominaciones de origen más prestigiosas.",
                "metadata": {"topic": "vinos_españoles", "category": "tintos"},
                "doc_id": "vinos_esp_1"
            },
            {
                "content": "El Tempranillo es la variedad de uva tinta más importante de España. Se caracteriza por sus aromas a frutas rojas y su capacidad de envejecimiento.",
                "metadata": {"topic": "uvas", "category": "tempranillo"},
                "doc_id": "tempranillo_1"
            },
            {
                "content": "Los vinos blancos de Rías Baixas con uva Albariño son perfectos para mariscos. Tienen alta acidez y aromas cítricos y minerales.",
                "metadata": {"topic": "vinos_blancos", "category": "albarino"},
                "doc_id": "albarino_1"
            },
            {
                "content": "Para almacenar vinos correctamente, mantener temperatura constante entre 12-15°C, humedad 70%, y evitar vibraciones y luz directa.",
                "metadata": {"topic": "conservacion", "category": "almacenamiento"},
                "doc_id": "conservacion_1"
            }
        ]
        
        self.documents = sample_docs
        await self._build_index()
    
    async def _build_index(self):
        """Construir índice TF-IDF de los documentos"""
        if not self.documents:
            return
            
        # Extraer contenido para vectorización
        texts = [doc["content"] for doc in self.documents]
        
        # Crear vectores TF-IDF
        self.doc_vectors = self.tfidf_vectorizer.fit_transform(texts)
        logger.info(f"Índice TF-IDF construido con {len(texts)} documentos")
    
    async def search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Buscar documentos usando TF-IDF"""
        if not self.documents or self.doc_vectors is None:
            return []
        
        try:
            # Vectorizar query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()
            
            # Obtener índices ordenados por relevancia
            top_indices = np.argsort(similarities)[::-1][:max_results]
            
            # Construir resultados
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Solo resultados con alguna similitud
                    doc = self.documents[idx].copy()
                    doc["relevance_score"] = float(similarities[idx])
                    results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    async def add_document(self, content: str, metadata: Optional[Dict] = None, doc_id: Optional[str] = None) -> str:
        """Agregar nuevo documento al índice"""
        if not doc_id:
            doc_id = f"doc_{len(self.documents)}"
        
        doc = {
            "content": content,
            "metadata": metadata or {},
            "doc_id": doc_id
        }
        
        self.documents.append(doc)
        await self._build_index()  # Reconstruir índice
        
        logger.info(f"Documento {doc_id} agregado. Total: {len(self.documents)}")
        return doc_id
    
    async def generate_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generar respuesta usando OpenAI con contexto"""
        if not self.openai_client:
            return f"Encontré {len(context_docs)} documentos relevantes, pero OpenAI no está configurado para generar respuesta detallada."
        
        # Construir contexto
        context_str = "\n\n".join([
            f"Documento {i+1}:\n{doc['content']}"
            for i, doc in enumerate(context_docs)
        ])
        
        # Crear prompt para el sumiller
        system_prompt = """Eres un sumiller experto y amigable. Tu trabajo es responder preguntas sobre vinos usando la información proporcionada.

Características de tus respuestas:
- Informativas pero accesibles para cualquier nivel de conocimiento
- Incluyes recomendaciones específicas cuando es relevante
- Mencionas maridajes cuando es apropiado
- Eres amigable y entusiasta sobre los vinos
- Si no tienes información suficiente, lo admites honestamente"""

        user_prompt = f"""Pregunta del usuario: {query}

Información disponible:
{context_str}

Por favor responde como sumiller experto usando esta información."""

        try:
            response = await self.openai_client.chat.completions.acreate(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generando respuesta OpenAI: {e}")
            return f"Error generando respuesta: {str(e)}"

# Instancia global
rag_engine = SimpleRAGEngine()

# FastAPI setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando RAG Server Simple...")
    await rag_engine.initialize()
    logger.info("RAG Server Simple iniciado exitosamente")
    yield
    # Shutdown
    logger.info("Cerrando RAG Server Simple...")

app = FastAPI(
    title="RAG MCP Server Simple",
    description="Sistema RAG sin base de datos vectorial, usando TF-IDF + OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "simple_tfidf",
        "documents_count": len(rag_engine.documents),
        "openai_configured": rag_engine.openai_client is not None
    }

@app.post("/query")
async def query_rag(query_data: QueryRequest):
    start_time = time.time()
    logger.info(f"Query recibida: {query_data.query}")

    try:
        # Buscar documentos relevantes
        relevant_docs = await rag_engine.search_documents(
            query_data.query, 
            query_data.max_results
        )
        
        # Generar respuesta
        if relevant_docs:
            response_text = await rag_engine.generate_response(
                query_data.query, 
                relevant_docs
            )
        else:
            response_text = "No encontré información relevante sobre tu consulta. ¿Podrías reformular la pregunta?"
        
        end_time = time.time()
        
        return {
            "answer": response_text,
            "sources": relevant_docs,
            "metadata": {
                "response_time": end_time - start_time,
                "source_count": len(relevant_docs),
                "mode": "simple_tfidf"
            }
        }
        
    except Exception as e:
        logger.error(f"Error procesando query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents")
async def add_document(doc_data: DocumentRequest):
    try:
        doc_id = await rag_engine.add_document(
            doc_data.content,
            doc_data.metadata,
            doc_data.doc_id
        )
        
        return {
            "message": "Documento agregado exitosamente",
            "doc_id": doc_id,
            "total_documents": len(rag_engine.documents)
        }
        
    except Exception as e:
        logger.error(f"Error agregando documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    return {
        "documents": [
            {
                "doc_id": doc["doc_id"],
                "content_preview": doc["content"][:100] + "...",
                "metadata": doc["metadata"]
            }
            for doc in rag_engine.documents
        ],
        "total_count": len(rag_engine.documents)
    }

if __name__ == "__main__":
    # Para desarrollo local
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "rag_server_simple:app",
        host="0.0.0.0",
        port=port,
        reload=True
    ) 