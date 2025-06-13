#!/usr/bin/env python3
"""
Script de inicio para el servidor RAG MCP principal
"""
import os
import uvicorn
from rag_mcp_server import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 