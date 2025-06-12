#!/usr/bin/env python3
"""
Script para probar las mejoras de performance y resiliencia
Ejecutar después de implementar los cambios
"""
import asyncio
import time
import httpx
import json
from typing import List, Dict
import logging
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUMILLER_URL = "http://localhost:8001"

class PerformanceTester:
    """Tester para verificar mejoras de performance"""
    
    def __init__(self):
        self.results = []
    
    async def test_single_request(self, session: httpx.AsyncClient, query: str) -> Dict:
        """Prueba una sola request y mide tiempo"""
        start_time = time.time()
        
        try:
            response = await session.post(
                f"{SUMILLER_URL}/query",
                json={"prompt": query, "user_id": "test_user"},
                timeout=30.0
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response_time": response_time,
                    "wines_found": data.get("wines_found", 0),
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": end_time - start_time,
                "error": str(e),
                "status_code": 0
            }
    
    async def test_without_pooling(self, queries: List[str]) -> List[Dict]:
        """Simula requests sin connection pooling (crear nueva conexión cada vez)"""
        logger.info("🔄 Testing SIN connection pooling...")
        results = []
        
        for i, query in enumerate(queries):
            # Crear nueva conexión para cada request
            async with httpx.AsyncClient() as client:
                logger.info(f"Request {i+1}/{len(queries)}: {query}")
                result = await self.test_single_request(client, query)
                results.append(result)
                logger.info(f"  ⏱️ {result['response_time']:.3f}s - {'✅' if result['success'] else '❌'}")
        
        return results
    
    async def test_with_pooling(self, queries: List[str]) -> List[Dict]:
        """Test con connection pooling (reutilizar conexión)"""
        logger.info("🚀 Testing CON connection pooling...")
        results = []
        
        # Una sola conexión para todas las requests
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        ) as client:
            for i, query in enumerate(queries):
                logger.info(f"Request {i+1}/{len(queries)}: {query}")
                result = await self.test_single_request(client, query)
                results.append(result)
                logger.info(f"  ⏱️ {result['response_time']:.3f}s - {'✅' if result['success'] else '❌'}")
        
        return results
    
    async def test_concurrent_requests(self, query: str, num_requests: int = 5) -> List[Dict]:
        """Test de requests concurrentes"""
        logger.info(f"🔀 Testing {num_requests} requests concurrentes...")
        
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        ) as client:
            tasks = []
            for i in range(num_requests):
                task = self.test_single_request(client, f"{query} #{i+1}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "success": False,
                        "error": str(result),
                        "response_time": 0
                    })
                else:
                    processed_results.append(result)
                
                logger.info(f"  Concurrent {i+1}: ⏱️ {processed_results[-1].get('response_time', 0):.3f}s")
            
            return processed_results
    
    async def test_circuit_breaker(self) -> Dict:
        """Test del circuit breaker (intentar conectar a servicio que no existe)"""
        logger.info("🔒 Testing circuit breaker...")
        
        # Intentar conectar a un puerto que no existe para disparar el circuit breaker
        fake_url = "http://localhost:9999"
        
        async with httpx.AsyncClient() as client:
            results = []
            
            for i in range(6):  # Más que el threshold (3)
                start_time = time.time()
                try:
                    response = await client.get(f"{fake_url}/health", timeout=2.0)
                    success = True
                except Exception as e:
                    success = False
                    error = str(e)
                
                end_time = time.time()
                
                result = {
                    "attempt": i + 1,
                    "success": success,
                    "response_time": end_time - start_time
                }
                
                if not success:
                    result["error"] = error
                
                results.append(result)
                logger.info(f"  Attempt {i+1}: {'✅' if success else '❌'} - {result['response_time']:.3f}s")
                
                # Pequeña pausa entre intentos
                await asyncio.sleep(0.5)
        
        return {"circuit_breaker_test": results}
    
    def analyze_results(self, results: List[Dict], test_name: str) -> Dict:
        """Analiza los resultados de performance"""
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", True)]
        
        if successful:
            response_times = [r["response_time"] for r in successful]
            stats = {
                "test_name": test_name,
                "total_requests": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(results) * 100,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times)
            }
            
            if len(response_times) > 1:
                stats["std_dev"] = statistics.stdev(response_times)
            else:
                stats["std_dev"] = 0
        else:
            stats = {
                "test_name": test_name,
                "total_requests": len(results),
                "successful": 0,
                "failed": len(failed),
                "success_rate": 0,
                "error": "No successful requests"
            }
        
        return stats
    
    async def test_health_endpoint(self) -> Dict:
        """Test del endpoint de health mejorado"""
        logger.info("🏥 Testing health endpoint...")
        
        async with httpx.AsyncClient() as client:
            try:
                start_time = time.time()
                response = await client.get(f"{SUMILLER_URL}/health")
                end_time = time.time()
                
                if response.status_code == 200:
                    health_data = response.json()
                    return {
                        "success": True,
                        "response_time": end_time - start_time,
                        "health_data": health_data
                    }
                else:
                    return {
                        "success": False,
                        "response_time": end_time - start_time,
                        "status_code": response.status_code,
                        "error": response.text
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

async def main():
    """Función principal del test"""
    print("🧪 TESTING DE MEJORAS DE PERFORMANCE")
    print("=" * 50)
    
    tester = PerformanceTester()
    
    # Queries de prueba
    test_queries = [
        "vino tinto para carne",
        "vino blanco ligero",
        "espumoso para celebrar",
        "vino económico buena calidad",
        "maridaje con paella"
    ]
    
    # 1. Test de health endpoint
    print("\n1️⃣ HEALTH ENDPOINT TEST")
    health_result = await tester.test_health_endpoint()
    if health_result["success"]:
        print(f"✅ Health check OK - {health_result['response_time']:.3f}s")
        if "health_data" in health_result:
            health_data = health_result["health_data"]
            print(f"   Status: {health_data.get('status', 'unknown')}")
            services = health_data.get('services', {})
            for service, status in services.items():
                print(f"   {service}: {'✅' if status else '❌'}")
            
            # Circuit breaker info
            if 'circuit_breaker' in health_data:
                cb = health_data['circuit_breaker']
                print(f"   Circuit Breaker: {cb.get('state', 'unknown')}")
    else:
        print(f"❌ Health check failed: {health_result.get('error', 'unknown')}")
        print("⚠️ El servidor podría no estar corriendo")
        return
    
    # 2. Test sin connection pooling (simulado)
    print("\n2️⃣ PERFORMANCE COMPARISON")
    without_pooling = await tester.test_without_pooling(test_queries[:3])
    stats_without = tester.analyze_results(without_pooling, "Sin Connection Pooling")
    
    # 3. Test con connection pooling
    with_pooling = await tester.test_with_pooling(test_queries[:3])
    stats_with = tester.analyze_results(with_pooling, "Con Connection Pooling")
    
    # 4. Test de requests concurrentes
    print("\n3️⃣ CONCURRENT REQUESTS TEST")
    concurrent_results = await tester.test_concurrent_requests("vino recomendado", 5)
    stats_concurrent = tester.analyze_results(concurrent_results, "Requests Concurrentes")
    
    # 5. Mostrar resultados comparativos
    print("\n📊 RESULTADOS COMPARATIVOS")
    print("=" * 50)
    
    def print_stats(stats):
        if "error" not in stats:
            print(f"  📈 {stats['test_name']}:")
            print(f"     Success Rate: {stats['success_rate']:.1f}%")
            print(f"     Avg Response: {stats['avg_response_time']:.3f}s")
            print(f"     Min Response: {stats['min_response_time']:.3f}s")
            print(f"     Max Response: {stats['max_response_time']:.3f}s")
            print(f"     Requests: {stats['successful']}/{stats['total_requests']}")
        else:
            print(f"  ❌ {stats['test_name']}: {stats['error']}")
    
    print_stats(stats_without)
    print_stats(stats_with)
    print_stats(stats_concurrent)
    
    # 6. Calcular mejoras
    if "error" not in stats_without and "error" not in stats_with:
        improvement = ((stats_without['avg_response_time'] - stats_with['avg_response_time']) 
                      / stats_without['avg_response_time'] * 100)
        print(f"\n🚀 MEJORA DE PERFORMANCE: {improvement:.1f}% más rápido con pooling")
        
        if improvement > 0:
            print("✅ Las optimizaciones están funcionando!")
        else:
            print("⚠️ No se detectó mejora significativa")
    
    # 7. Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    
    if stats_with.get('avg_response_time', 0) > 2.0:
        print("⚠️ Tiempo de respuesta alto (>2s) - considera optimizar queries RAG")
    else:
        print("✅ Tiempo de respuesta aceptable")
    
    if stats_concurrent.get('success_rate', 0) < 90:
        print("⚠️ Baja tasa de éxito en requests concurrentes - revisa timeouts")
    else:
        print("✅ Buena resiliencia en requests concurrentes")
    
    print(f"\n🏁 Testing completado - {len(test_queries)} queries probadas")

if __name__ == "__main__":
    asyncio.run(main())