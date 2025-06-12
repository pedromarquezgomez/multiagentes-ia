#!/usr/bin/env python3
"""
Script para cargar vinos masivamente desde JSON a ChromaDB
"""
import json
import requests
import time
from pathlib import Path

# Configuración
RAG_MCP_URL = "http://localhost:8000"
WINES_FILE = "mcp-agentic-rag/knowledge_base/vinos.json"

def load_wines_data():
    """Cargar datos de vinos desde JSON"""
    try:
        with open(WINES_FILE, 'r', encoding='utf-8') as f:
            wines = json.load(f)
        print(f"✅ Cargados {len(wines)} vinos desde {WINES_FILE}")
        return wines
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")
        return []

def create_wine_content(wine):
    """Crear contenido descriptivo para el vino"""
    content = f"""
Vino: {wine['name']}
Tipo: {wine['type']}
Región: {wine['region']}
Añada: {wine.get('vintage', 'N/A')}
Precio: {wine.get('price', 0):.2f}€
Stock: {wine.get('stock', 0)} unidades
Descripción: {wine.get('description', 'Sin descripción')}
Maridaje: {wine.get('pairing', 'Sin maridaje específico')}
Puntuación: {wine.get('rating', 0)}/100
""".strip()
    return content

def upload_wine_to_rag(wine, index):
    """Subir un vino al RAG MCP Server"""
    try:
        content = create_wine_content(wine)
        doc_id = f"wine_{index}_{wine['name'].replace(' ', '_').lower()}"
        
        # Preparar metadata
        metadata = {
            "name": wine['name'],
            "type": wine['type'],
            "region": wine['region'],
            "vintage": wine.get('vintage'),
            "price": wine.get('price'),
            "stock": wine.get('stock'),
            "rating": wine.get('rating'),
            "pairing": wine.get('pairing', ''),
            "doc_type": "wine"
        }
        
        # Payload para la API
        payload = {
            "content": content,
            "metadata": metadata,
            "doc_id": doc_id
        }
        
        # Enviar a RAG MCP Server
        response = requests.post(
            f"{RAG_MCP_URL}/documents",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return True, doc_id
        else:
            return False, f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, str(e)

def test_rag_connection():
    """Probar conexión al RAG MCP Server"""
    try:
        response = requests.get(f"{RAG_MCP_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Conexión al RAG MCP Server exitosa")
            return True
        else:
            print(f"❌ RAG MCP Server respondió con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al RAG MCP Server: {e}")
        return False

def main():
    print("🍷 CARGADOR MASIVO DE VINOS - MCP Agentic RAG")
    print("=" * 50)
    
    # Verificar conexión
    if not test_rag_connection():
        print("❌ No se puede conectar al RAG MCP Server")
        print("💡 Asegúrate de que el sistema esté iniciado: ./start-local.sh")
        return
    
    # Cargar datos
    wines = load_wines_data()
    if not wines:
        return
    
    # Cargar vinos
    successful = 0
    failed = 0
    
    print(f"\n🚀 Iniciando carga de {len(wines)} vinos...")
    
    for i, wine in enumerate(wines, 1):
        print(f"📦 Cargando {i}/{len(wines)}: {wine['name']}", end="... ")
        
        success, result = upload_wine_to_rag(wine, i)
        
        if success:
            print("✅")
            successful += 1
        else:
            print(f"❌ {result}")
            failed += 1
        
        # Pausa pequeña para no sobrecargar
        if i % 10 == 0:
            time.sleep(0.5)
            print(f"   📊 Progreso: {i}/{len(wines)} ({(i/len(wines)*100):.1f}%)")
    
    print(f"\n🎉 CARGA COMPLETADA:")
    print(f"   ✅ Exitosos: {successful}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   📊 Total: {len(wines)}")
    
    if successful > 0:
        print(f"\n🧪 Probando búsqueda...")
        test_search()

def test_search():
    """Probar búsqueda después de la carga"""
    test_queries = [
        "vino tinto rioja",
        "vino blanco para mariscos",
        "vino económico",
        "espumoso para celebrar"
    ]
    
    for query in test_queries:
        try:
            response = requests.post(
                f"{RAG_MCP_URL}/query",
                json={"query": query, "max_results": 2},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                sources_count = len(data.get('sources', []))
                print(f"   🔍 '{query}': {sources_count} vinos encontrados")
            else:
                print(f"   ❌ Error buscando '{query}': {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error buscando '{query}': {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main() 