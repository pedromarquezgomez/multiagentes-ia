# sumiller-bot/http_client.py
"""
HTTP Client Pool con Circuit Breaker y Retry Logic
Código completo para mejorar performance y resiliencia
"""
import httpx
import asyncio
import time
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Estados del Circuit Breaker"""
    CLOSED = "closed"      # Funcionando normal
    OPEN = "open"          # Fallando, no hacer requests
    HALF_OPEN = "half_open"  # Probando si se recuperó

class CircuitBreaker:
    """
    Circuit breaker para prevenir cascading failures
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """Ejecuta función con circuit breaker protection"""
        async with self._lock:
            # Si está abierto, verificar si es hora de probar
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time < self.timeout:
                    remaining_time = self.timeout - (time.time() - self.last_failure_time)
                    raise Exception(f"Circuit breaker OPEN. Próximo intento en {remaining_time:.1f}s")
                else:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("🔄 Circuit breaker cambió a HALF_OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Si funciona, resetear
            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info("✅ Circuit breaker CERRADO - servicio recuperado")
            
            return result
            
        except Exception as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                # Si superamos el threshold, abrir circuit
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.error(f"🚨 Circuit breaker ABIERTO después de {self.failure_count} fallos")
            
            raise e

class HTTPClientPool:
    """
    Pool de conexiones HTTP reutilizables para reducir latencia
    """
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()
    
    async def get_client(self) -> httpx.AsyncClient:
        """Obtiene cliente HTTP reutilizable con connection pooling"""
        if self._client is None:
            async with self._lock:
                if self._client is None:  # Double-check locking
                    self._client = httpx.AsyncClient(
                        # 🔥 CONFIGURACIÓN CRÍTICA DE PERFORMANCE
                        limits=httpx.Limits(
                            max_connections=100,      # Máximo conexiones simultáneas
                            max_keepalive_connections=20,  # Conexiones que se mantienen vivas
                            keepalive_expiry=30.0,    # Tiempo de vida de conexiones (segundos)
                        ),
                        timeout=httpx.Timeout(
                            connect=5.0,    # Tiempo máximo para conectar
                            read=30.0,      # Tiempo máximo para leer respuesta
                            write=5.0,      # Tiempo máximo para escribir request
                            pool=10.0       # Tiempo máximo esperando conexión del pool
                        ),
                        # 🚀 OPTIMIZACIONES ADICIONALES
                        verify=True,                  # Verificar certificados SSL
                        follow_redirects=True,        # Seguir redirects automáticamente
                        headers={
                            "User-Agent": "SumillerBot/3.1",
                            "Connection": "keep-alive",
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        }
                    )
                    logger.info("✅ HTTP Client Pool inicializado")
        
        return self._client
    
    async def close(self):
        """Cierra el pool de conexiones"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("🔒 HTTP Client Pool cerrado")

class ResilientHTTPClient:
    """
    Cliente HTTP con retry, circuit breaker y connection pooling
    """
    
    def __init__(self):
        self.pool = HTTPClientPool()
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30.0)
        
    async def post_with_retry(self, url: str, json_data: dict, max_retries: int = 3) -> dict:
        """
        POST con retry exponential backoff y circuit breaker
        """
        
        async def _make_request():
            client = await self.pool.get_client()
            response = await client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()
        
        # Intentar con circuit breaker
        for attempt in range(max_retries):
            try:
                return await self.circuit_breaker.call(_make_request)
                
            except Exception as e:
                if attempt == max_retries - 1:  # Último intento
                    logger.error(f"❌ Falló después de {max_retries} intentos: {e}")
                    raise
                
                # Exponential backoff: 1s, 2s, 4s...
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Intento {attempt + 1} falló, reintentando en {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
    
    async def get_with_retry(self, url: str, max_retries: int = 3) -> dict:
        """GET con retry y circuit breaker"""
        
        async def _make_request():
            client = await self.pool.get_client()
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        
        for attempt in range(max_retries):
            try:
                return await self.circuit_breaker.call(_make_request)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ GET intento {attempt + 1} falló, reintentando en {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
    
    async def get_simple(self, url: str) -> dict:
        """GET simple sin retry (para health checks)"""
        client = await self.pool.get_client()
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Cierra el cliente resiliente"""
        await self.pool.close()
    
    def get_circuit_info(self) -> Dict[str, Any]:
        """Obtiene información del estado del circuit breaker"""
        return {
            "state": self.circuit_breaker.state.value,
            "failure_count": self.circuit_breaker.failure_count,
            "last_failure_time": self.circuit_breaker.last_failure_time,
            "threshold": self.circuit_breaker.failure_threshold,
            "timeout": self.circuit_breaker.timeout
        }

# Instancia global resiliente
resilient_client = ResilientHTTPClient()

# Funciones helper para facilitar uso
async def get_http_client() -> httpx.AsyncClient:
    """Función helper para obtener cliente HTTP"""
    return await resilient_client.pool.get_client()

async def close_http_pool():
    """Función helper para cerrar el pool"""
    await resilient_client.close()

async def post_resilient(url: str, json_data: dict, max_retries: int = 3) -> dict:
    """Función helper para POST resiliente"""
    return await resilient_client.post_with_retry(url, json_data, max_retries)

async def get_resilient(url: str, max_retries: int = 3) -> dict:
    """Función helper para GET resiliente"""
    return await resilient_client.get_with_retry(url, max_retries)