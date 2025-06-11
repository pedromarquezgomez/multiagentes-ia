#!/usr/bin/env python3
"""
Configuración Multi-Entorno para Sumy Wine Recommender
Detecta automáticamente si estamos en local o Cloud Run y configura URLs.
"""
import os

class Config:
    """Configuración inteligente que se adapta al entorno."""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.setup_urls()
        
    def _detect_environment(self) -> str:
        """Detecta automáticamente el entorno de ejecución."""
        # Cloud Run tiene estas variables específicas
        if os.getenv('K_SERVICE') or os.getenv('GOOGLE_CLOUD_PROJECT'):
            return 'cloud'
        
        # Si hay variable explícita
        env = os.getenv('ENVIRONMENT', '').lower()
        if env in ['local', 'cloud']:
            return env
            
        # Por defecto asumimos local
        return 'local'
    
    def setup_urls(self):
        """Configura URLs según el entorno."""
        if self.environment == 'cloud':
            self.setup_cloud_urls()
        else:
            self.setup_local_urls()
            
    def setup_local_urls(self):
        """Configuración para entorno local (Docker Compose)."""
        self.sumiller_port = int(os.getenv('SUMILLER_PORT', '8001'))
        self.rag_mcp_port = int(os.getenv('RAG_MCP_PORT', '8000'))
        self.memory_mcp_port = int(os.getenv('MEMORY_MCP_PORT', '8002'))
        self.ui_port = int(os.getenv('UI_PORT', '3000'))
        
        # URLs internas para Docker Compose
        self.sumiller_url = f"http://sumiller-bot:{self.sumiller_port}"
        self.rag_mcp_url = f"http://rag-mcp-server:{self.rag_mcp_port}"
        self.memory_mcp_url = f"http://memory-mcp-server:{self.memory_mcp_port}"
        
        # URL externa para UI (localhost)
        self.sumiller_external_url = f"http://localhost:{self.sumiller_port}"
        
    def setup_cloud_urls(self):
        """Configuración para Cloud Run."""
        # En Cloud Run, obtenemos las URLs de variables de entorno
        self.sumiller_url = os.getenv('CLOUD_SUMILLER_URL', 'http://localhost:8001')
        self.rag_mcp_url = os.getenv('CLOUD_RAG_MCP_URL', 'http://localhost:8000')
        self.memory_mcp_url = os.getenv('CLOUD_MEMORY_MCP_URL', 'http://localhost:8002')
        
        # En Cloud Run, URLs internas y externas son las mismas
        self.sumiller_external_url = self.sumiller_url
        
        # Puerto desde variable de entorno (Cloud Run)
        self.port = int(os.getenv('PORT', '8080'))
    
    def get_openai_key(self):
        """Obtiene la API key de OpenAI de forma segura."""
        # Prioridad: 1) Secreto montado, 2) Variable de entorno
        secret_path = "/run/secrets/openai-api-key"
        if os.path.exists(secret_path):
            with open(secret_path, "r") as f:
                return f.read().strip()
        return os.getenv('OPENAI_API_KEY')
    
    def get_service_url(self, service_name: str) -> str:
        """Obtiene la URL de un servicio específico."""
        if service_name == 'sumiller':
            return self.sumiller_url
        elif service_name == 'rag-mcp':
            return self.rag_mcp_url
        elif service_name == 'memory-mcp':
            return self.memory_mcp_url
        # Compatibilidad con nombres antiguos
        elif service_name == 'mcp':
            return self.rag_mcp_url  # Redirigir al nuevo RAG MCP
        else:
            raise ValueError(f"Servicio desconocido: {service_name}")
    
    def is_local(self) -> bool:
        """Verifica si estamos en entorno local."""
        return self.environment == 'local'
    
    def is_cloud(self) -> bool:
        """Verifica si estamos en Cloud Run."""
        return self.environment == 'cloud'
    
    def __str__(self):
        """Representación string para debugging."""
        return f"""
Config Summary:
  Environment: {self.environment}
  Sumiller URL: {self.sumiller_url}
  RAG MCP URL: {self.rag_mcp_url}
  Memory MCP URL: {self.memory_mcp_url}
  OpenAI Key: {'✓ Configured' if self.get_openai_key() else '✗ Missing'}
        """.strip()

# Instancia global
config = Config()

# Para debugging
if __name__ == "__main__":
    print(config) 