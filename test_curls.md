# 🍷 Curls de Testing para el Sistema Sumiller

## 🔍 Health Checks

```bash
# Health Check Sumiller
curl -s "https://sumiller-bot-production.up.railway.app/health" | jq .

# Health Check RAG Server
curl -s "https://rag-mcp-server-production.up.railway.app/health" | jq .
```

## 🎯 Clasificación de Queries

```bash
# Clasificar query de vino
curl -X POST "https://sumiller-bot-production.up.railway.app/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "vino tinto español", "user_id": "test"}' | jq .

# Clasificar query de comida
curl -X POST "https://sumiller-bot-production.up.railway.app/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "paella de marisco", "user_id": "test"}' | jq .
```

## 🍷 Consultas al Sumiller

```bash
# Consulta simple de vino
curl -X POST "https://sumiller-bot-production.up.railway.app/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un vino tinto español", "user_id": "test"}' | jq .

# Consulta con contexto
curl -X POST "https://sumiller-bot-production.up.railway.app/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino va bien con paella?", "user_id": "test", "context": "Estoy en un restaurante de marisco"}' | jq .
```

## 🧠 Memoria y Contexto

```bash
# Obtener historial de usuario
curl -X GET "https://sumiller-bot-production.up.railway.app/memory/test" | jq .

# Limpiar memoria de usuario
curl -X DELETE "https://sumiller-bot-production.up.railway.app/memory/test" | jq .
```

## 🔍 RAG y Embeddings

```bash
# Consulta directa a RAG (⚠️ Actualmente devuelve 502)
curl -X POST "https://rag-mcp-server-production.up.railway.app/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "vino tinto", "max_results": 3}' | jq .

# Stats del RAG Server (⚠️ Actualmente devuelve 502)
curl -s "https://rag-mcp-server-production.up.railway.app/stats" | jq .
```

## 🎯 Casos de Uso Completos

```bash
# 1. Clasificar y consultar vino
curl -X POST "https://sumiller-bot-production.up.railway.app/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "vino tinto rioja", "user_id": "test"}' | jq .

curl -X POST "https://sumiller-bot-production.up.railway.app/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino tinto de Rioja me recomiendas?", "user_id": "test"}' | jq .

# 2. Clasificar y consultar comida
curl -X POST "https://sumiller-bot-production.up.railway.app/classify" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "paella valenciana", "user_id": "test"}' | jq .

curl -X POST "https://sumiller-bot-production.up.railway.app/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino va bien con paella valenciana?", "user_id": "test"}' | jq .
```

## 📊 Diagnóstico Completo

```bash
# Test completo de embeddings
./test_embeddings.sh

# Test completo del sistema
./test_curl_completo.sh
```

## 💡 Tips de Uso

1. **Añadir `| jq .`** al final de cada curl para formatear la salida JSON
2. **Cambiar `test`** por un ID de usuario real para probar la memoria
3. **Modificar el prompt** para probar diferentes tipos de consultas
4. **Añadir `-v`** para ver los headers y detalles de la petición
5. **Usar `-i`** para ver los headers de respuesta

## 🔧 Troubleshooting

Si algún endpoint falla:

1. **Verificar que los servicios están en línea:**
   ```bash
   curl -s "https://sumiller-bot-production.up.railway.app/health" | jq .
   ```

2. **Si el RAG server devuelve 502:**
   - El servicio está en proceso de inicialización
   - ChromaDB está cargando los embeddings
   - El sistema seguirá funcionando sin RAG (fallback a OpenAI)
   - Esperar unos minutos y volver a intentar

3. **Verificar la memoria:**
   ```bash
   curl -X GET "https://sumiller-bot-production.up.railway.app/memory/test" | jq .
   ```

4. **Revisar los logs del servicio en Railway:**
   ```bash
   railway service rag-mcp-server
   railway logs
   ```

5. **Si el problema persiste:**
   - El sumiller seguirá funcionando sin RAG
   - Las respuestas serán más genéricas pero funcionales
   - Se puede usar el sistema mientras se resuelve el RAG 