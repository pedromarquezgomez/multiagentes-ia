#!/usr/bin/env python3
"""
Configuración Multi-Entorno para Sumy Wine Recommender
Detecta automáticamente si estamos en local, Cloud Run o Railway y configura URLs.
"""
import os

class Config:
    """Configuración inteligente que se adapta al entorno."""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.setup_urls()
        
    def _detect_environment(self) -> str:
        """Detecta automáticamente el entorno de ejecución."""
        # Railway tiene estas variables específicas
        if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
            return 'railway'
        
        # Cloud Run tiene estas variables específicas
        if os.getenv('K_SERVICE') or os.getenv('GOOGLE_CLOUD_PROJECT'):
            return 'cloud'
        
        # Si hay variable explícita
        env = os.getenv('ENVIRONMENT', '').lower()
        if env in ['local', 'cloud', 'railway']:
            return env
            
        # Por defecto asumimos local
        return 'local'
    
    def setup_urls(self):
        """Configura URLs según el entorno."""
        if self.environment == 'railway':
            self.setup_railway_urls()
        elif self.environment == 'cloud':
            self.setup_cloud_urls()
        else:
            self.setup_local_urls()
            
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

    def setup_railway_urls(self):
        """🚂 NUEVA: Configuración para Railway."""
        # En Railway, las URLs las proporciona Railway automáticamente
        self.rag_mcp_url = os.getenv('RAG_MCP_URL', 'http://localhost:8000')
        self.memory_mcp_url = os.getenv('MEMORY_MCP_URL', 'http://localhost:8002')
        
        # El sumiller usa estas URLs para comunicarse con otros servicios
        self.maitre_url = self.rag_mcp_url  # Por compatibilidad
        self.sumiller_url = os.getenv('SUMILLER_URL', f"http://localhost:{os.getenv('PORT', '8001')}")
        self.mcp_server_url = self.memory_mcp_url
        
        # Puerto dinámico de Railway
        self.port = int(os.getenv('PORT', '8001'))
        
        # Configuración optimizada para Railway
        self.max_retries = 3
        self.timeout = 30
        
        # URL externa (Railway la genera automáticamente)
        self.maitre_external_url = self.rag_mcp_url
        
        # Variables específicas de Railway
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        
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
        return os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
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
        elif service_name == 'rag':  # 🚂 NUEVO para Railway
            return getattr(self, 'rag_mcp_url', self.maitre_url)
        elif service_name == 'memory':  # 🚂 NUEVO para Railway
            return getattr(self, 'memory_mcp_url', self.mcp_server_url)
        else:
            raise ValueError(f"Servicio desconocido: {service_name}")
    
    def is_local(self) -> bool:
        """Verifica si estamos en entorno local."""
        return self.environment == 'local'
    
    def is_cloud(self) -> bool:
        """Verifica si estamos en Cloud Run."""
        return self.environment == 'cloud'
    
    def is_railway(self) -> bool:
        """🚂 NUEVO: Verifica si estamos en Railway."""
        return self.environment == 'railway'
    
    def get_port(self) -> int:
        """Obtiene el puerto según el entorno."""
        if self.is_railway():
            return self.port
        elif self.is_cloud():
            return getattr(self, 'port', 8080)
        else:
            return getattr(self, 'sumiller_port', 8001)
    
    def __str__(self):
        """Representación string para debugging."""
        base_info = f"""
Config Summary:
  Environment: {self.environment}
  Port: {self.get_port()}
  OpenAI Key: {'✓ Configured' if self.get_openai_key() else '✗ Missing'}
  OpenAI Base URL: {self.get_openai_base_url()}
  OpenAI Model: {self.get_openai_model()}
        """.strip()
        
        # Información específica por entorno
        if self.is_railway():
            railway_info = f"""
  RAG MCP URL: {getattr(self, 'rag_mcp_url', 'Not set')}
  Memory MCP URL: {getattr(self, 'memory_mcp_url', 'Not set')}
  Timeout: {getattr(self, 'timeout', 30)}s
  Max Retries: {getattr(self, 'max_retries', 3)}
            """.strip()
            return base_info + "\n" + railway_info
        elif self.is_local():
            local_info = f"""
  Maitre URL: {getattr(self, 'maitre_url', 'Not set')}
  Sumiller URL: {getattr(self, 'sumiller_url', 'Not set')}
  MCP Server URL: {getattr(self, 'mcp_server_url', 'Not set')}
            """.strip()
            return base_info + "\n" + local_info
        else:
            return base_info

# Instancia global
config = Config()

# Para debugging
if __name__ == "__main__":
    print("🔧 Configuración actual:")
    print(config)
    print(f"\n🌐 Entorno detectado: {config.environment}")
    print(f"🚪 Puerto: {config.get_port()}")
    
    if config.is_railway():
        print("🚂 Configuración Railway activa")
    elif config.is_local():
        print("🏠 Configuración local activa")
    elif config.is_cloud():
        print("☁️ Configuración cloud activa")