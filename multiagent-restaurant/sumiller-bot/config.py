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
        
        # Railway environment
        if os.getenv('RAILWAY_ENVIRONMENT'):
            return 'railway'
        
        # Si hay variable explícita
        env = os.getenv('ENVIRONMENT', '').lower()
        if env in ['local', 'cloud', 'railway']:
            return env
            
        # Por defecto asumimos local
        return 'local'
    
    def setup_urls(self):
        """Configura URLs según el entorno."""
        if self.environment == 'cloud':
            self.setup_cloud_urls()
        elif self.environment == 'railway':
            self.setup_railway_urls()
        else:
            self.setup_local_urls()
    
    def setup_railway_urls(self):
        """Configuración para Railway."""
        # URLs desde variables de entorno de Railway
        self.rag_mcp_url = os.getenv('RAG_MCP_URL', 'https://rag-mcp-server-production.up.railway.app')
        self.memory_mcp_url = os.getenv('MEMORY_MCP_URL', 'https://memory-mcp-server-production.up.railway.app')
        
        # Puerto desde variable de entorno (Railway)
        self.port = int(os.getenv('PORT', '8000'))
            
    def setup_local_urls(self):
        """Configuración para entorno local (Docker Compose)."""
        self.maitre_port = int(os.getenv('MAITRE_PORT', '8000'))
        self.sumiller_port = int(os.getenv('SUMILLER_PORT', '8001'))
        self.mcp_port = int(os.getenv('MCP_SERVER_PORT', '8002'))
        self.ui_port = int(os.getenv('UI_PORT', '3000'))
        
        # URLs internas para Docker Compose
        self.maitre_url = f"http://maitre-bot:{self.maitre_port}"
        self.sumiller_url = f"http://sumiller-bot:{self.sumiller_port}"
        self.mcp_server_url = f"http://mcp-server:{self.mcp_port}"
        
        # URL externa para UI (localhost)
        self.maitre_external_url = f"http://localhost:{self.maitre_port}"
        
    def setup_cloud_urls(self):
        """Configuración para Cloud Run."""
        # En Cloud Run, obtenemos las URLs de variables de entorno
        self.maitre_url = os.getenv('CLOUD_MAITRE_URL', os.getenv('SUMILLER_URL', 'http://localhost:8000'))
        self.sumiller_url = os.getenv('CLOUD_SUMILLER_URL', os.getenv('MCP_SERVER_URL', 'http://localhost:8001'))
        self.mcp_server_url = os.getenv('CLOUD_MCP_SERVER_URL', 'http://localhost:8002')
        
        # En Cloud Run, URLs internas y externas son las mismas
        self.maitre_external_url = self.maitre_url
        
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
    
    def get_openai_base_url(self):
        """Obtiene la base URL de OpenAI."""
        return os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    
    def get_openai_model(self):
        """Obtiene el modelo de OpenAI a usar."""
        return os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def get_deepseek_key(self):
        """Obtiene la API key de DeepSeek de forma segura."""
        # Prioridad: 1) Secreto montado, 2) Variable de entorno
        secret_path = "/run/secrets/deepseek-api-key"
        if os.path.exists(secret_path):
            with open(secret_path, "r") as f:
                return f.read().strip()
        return os.getenv('DEEPSEEK_API_KEY')
    
    def get_deepseek_base_url(self):
        """Obtiene la base URL de DeepSeek."""
        return os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    def get_deepseek_model(self):
        """Obtiene el modelo de DeepSeek a usar."""
        return os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    def get_service_url(self, service_name: str) -> str:
        """Obtiene la URL de un servicio específico."""
        if service_name == 'maitre':
            return self.maitre_url
        elif service_name == 'sumiller':
            return self.sumiller_url
        elif service_name == 'mcp':
            return self.mcp_server_url
        else:
            raise ValueError(f"Servicio desconocido: {service_name}")
    
    def is_local(self) -> bool:
        """Verifica si estamos en entorno local."""
        return self.environment == 'local'
    
    def is_cloud(self) -> bool:
        """Verifica si estamos en Cloud Run."""
        return self.environment == 'cloud'
    
    def is_railway(self) -> bool:
        """Verifica si estamos en Railway."""
        return self.environment == 'railway'
    
    def __str__(self):
        """Representación string para debugging."""
        return f"""
Config Summary:
  Environment: {self.environment}
  OpenAI Key: {'✓ Configured' if self.get_openai_key() else '✗ Missing'}
  OpenAI Base URL: {self.get_openai_base_url()}
  OpenAI Model: {self.get_openai_model()}
  DeepSeek Key: {'✓ Configured' if self.get_deepseek_key() else '✗ Missing'}
  DeepSeek Base URL: {self.get_deepseek_base_url()}
  DeepSeek Model: {self.get_deepseek_model()}
        """.strip()

# Instancia global
config = Config()

# Para debugging
if __name__ == "__main__":
    print(config) 