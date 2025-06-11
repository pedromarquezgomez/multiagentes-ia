#!/usr/bin/env python3
"""
Script para cargar teoría de sumiller al sistema RAG
"""
import requests
import re

RAG_MCP_URL = "http://localhost:8000"
TEORIA_FILE = "mcp-agentic-rag/knowledge_base/teoria_sumiller.txt"

def load_teoria():
    """Cargar teoría de sumiller por secciones"""
    try:
        with open(TEORIA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir por secciones principales (identificadas por números romanos)
        sections = re.split(r'\n(?=[IVX]+\.)', content)
        
        successful = 0
        total_sections = len(sections)
        
        print(f"📚 Cargando {total_sections} secciones de teoría sumiller...")
        
        for i, section in enumerate(sections):
            if section.strip():
                # Extraer título de la sección
                lines = section.strip().split('\n')
                title = lines[0] if lines else f"Sección {i+1}"
                
                payload = {
                    'content': section.strip(),
                    'metadata': {
                        'doc_type': 'teoria_sumiller',
                        'section_title': title,
                        'section_number': i+1,
                        'category': 'formacion_profesional',
                        'source': 'manual_sumiller'
                    },
                    'doc_id': f'teoria_sumiller_section_{i+1:02d}'
                }
                
                try:
                    response = requests.post(
                        f"{RAG_MCP_URL}/documents",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        successful += 1
                        print(f"✅ Sección {i+1}: {title}")
                    else:
                        print(f"❌ Error en sección {i+1}: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error en sección {i+1}: {e}")
        
        print(f"\n🎉 TEORÍA CARGADA:")
        print(f"   ✅ Exitosos: {successful}/{total_sections}")
        print(f"   📚 Base de conocimiento ampliada con formación profesional")
        
        # Probar búsqueda de conceptos
        test_teoria_search()
        
    except Exception as e:
        print(f"❌ Error cargando teoría: {e}")

def test_teoria_search():
    """Probar búsqueda de conceptos de teoría"""
    print(f"\n🧪 Probando acceso a la teoría...")
    
    test_queries = [
        "qué es un sumiller",
        "técnicas de cata",
        "temperatura de servicio",
        "maridaje de vinos",
        "conservación del vino"
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
                sources = data.get('sources', [])
                teoria_sources = [s for s in sources if s.get('metadata', {}).get('doc_type') == 'teoria_sumiller']
                print(f"   🔍 '{query}': {len(teoria_sources)} conceptos encontrados")
            else:
                print(f"   ❌ Error buscando '{query}': {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error buscando '{query}': {e}")

if __name__ == "__main__":
    print("🍷 CARGADOR DE TEORÍA SUMILLER")
    print("=" * 40)
    load_teoria() 