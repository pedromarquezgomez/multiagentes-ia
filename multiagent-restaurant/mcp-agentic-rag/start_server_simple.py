#!/usr/bin/env python3
"""
Servidor RAG MCP Simple para Testing
"""
import os
import uvicorn
from fastapi import FastAPI

# Crear app básica
app = FastAPI(title="RAG MCP Server - Simple")

@app.get("/health")
async def health():
    return {
        "status": "operational",
        "service": "rag-mcp-server-simple",
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

@app.post("/query")
async def query(request: dict):
    return {
        "answer": f"RAG respuesta simple para: {request.get('query', 'Sin consulta')}",
        "sources": [],
        "context_used": {"simple": True}
    }

@app.get("/")
async def root():
    return {"message": "RAG MCP Server funcionando"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 