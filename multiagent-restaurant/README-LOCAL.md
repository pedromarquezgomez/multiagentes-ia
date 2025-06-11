# 🍷 Sumy Wine Recommender - Despliegue Local

Sistema de recomendación de vinos con **MCP Agentic RAG** y memoria conversacional.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI Frontend   │    │   Sumiller Bot   │    │  RAG MCP Server │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8001     │    │   Port: 8000    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Memory MCP Server│    │    ChromaDB     │
                       │   (FastAPI)      │    │  (Vector DB)    │
                       │   Port: 8002     │    │   Port: 8004    │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │      Redis       │
                       │   (Memory)       │
                       │   Port: 6379     │
                       └──────────────────┘
```

## 🚀 Inicio Rápido

### 1. Prerrequisitos
- Docker Desktop instalado y corriendo
- API Key de OpenAI
- Puertos libres: 3000, 6379, 8000-8004

### 2. Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Crea el archivo .env
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-openai-api-key-here
ENVIRONMENT=local
EOF
```

### 3. Inicio del Sistema

```bash
# Ejecutar el script de inicio
./start-local.sh
```

El script automáticamente:
- ✅ Verifica Docker y dependencias
- ✅ Limpia contenedores anteriores
- ✅ Construye las imágenes
- ✅ Inicia todos los servicios
- ✅ Verifica que estén funcionando

## 📋 Servicios Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| 🌐 **UI Frontend** | http://localhost:3000 | Interfaz web principal |
| 🤖 **Sumiller Bot** | http://localhost:8001 | API de recomendaciones |
| 🧠 **RAG MCP Server** | http://localhost:8000 | Búsqueda semántica agéntica |
| 💾 **Memory MCP Server** | http://localhost:8002 | Memoria conversacional |
| 🧪 **MCP Tester** | http://localhost:8003 | Interfaz de testing |
| 📊 **ChromaDB** | http://localhost:8004 | Base de datos vectorial |

## 🧪 Testing del Sistema

### Tests Automáticos
```bash
# Verificar estado de todos los servicios
./tester.sh health

# Prueba completa del flujo agéntico
./tester.sh flow

# Test específico del RAG MCP
./tester.sh rag

# Test de memoria conversacional
./tester.sh memory
```

### Tests Manuales

#### 1. Verificar RAG MCP Server
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "vino tinto argentino", "user_id": "test"}'
```

#### 2. Verificar Memory MCP Server
```bash
curl -X POST "http://localhost:8002/save" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "interaction": "Prefiero vinos tintos"}'
```

#### 3. Verificar Sumiller Bot
```bash
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "recomiéndame un vino para asado", "user_id": "test"}'
```

## 🛠️ Comandos de Gestión

### Ver Logs
```bash
# Logs de todos los servicios
docker compose logs -f

# Logs específicos
docker compose logs -f sumiller-bot
docker compose logs -f rag-mcp-server
docker compose logs -f memory-mcp-server
```

### Reiniciar Servicios
```bash
# Reiniciar todo
docker compose restart

# Reiniciar servicio específico
docker compose restart sumiller-bot
```

### Detener y Limpiar
```bash
# Detener servicios
docker compose down

# Limpiar todo (incluyendo volúmenes)
docker compose down -v --remove-orphans
```

## 🔧 Configuración Avanzada

### Variables de Entorno Disponibles

```bash
# APIs
OPENAI_API_KEY=sk-xxx           # Requerida

# Puertos (opcional, usa defaults)
SUMILLER_PORT=8001
RAG_MCP_PORT=8000
MEMORY_MCP_PORT=8002
UI_PORT=3000

# Base de datos
VECTOR_DB_TYPE=chroma
REDIS_URL=redis://redis:6379

# Debug
LOG_LEVEL=INFO
DEBUG=false
```

### Estructura de Archivos
```
multiagent-restaurant/
├── docker-compose.yaml         # Configuración principal
├── start-local.sh             # Script de inicio
├── tester.sh                  # Suite de testing
├── config.py                  # Configuración multi-entorno
├── mcp-agentic-rag/          # Sistema MCP RAG
├── sumiller-bot/             # Bot principal actualizado
└── ui/                       # Frontend React
```

## 🐛 Solución de Problemas

### Puerto ocupado
```bash
# Verificar qué proceso usa el puerto
lsof -i :8000

# Matar proceso específico
kill -9 <PID>
```

### Error de conexión a OpenAI
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Probar conexión
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Problemas con ChromaDB
```bash
# Limpiar datos vectoriales
docker compose down -v
docker volume rm multiagent-restaurant_chromadb_data
```

### Logs de debugging
```bash
# Logs detallados de un servicio
docker compose logs --tail=100 -f rag-mcp-server
```

## 🎯 Características del Sistema

### 🧠 Capacidades Agénticas
- **Expansión de consultas**: Mejora automáticamente las búsquedas del usuario
- **Memoria conversacional**: Recuerda preferencias y contexto
- **Búsqueda semántica**: Encuentra vinos relevantes usando embeddings
- **Personalización**: Adapta recomendaciones por usuario
- **Fallbacks**: Sistema robusto con respaldos automáticos

### 🔄 Flujo de Procesamiento
1. Usuario hace consulta en UI
2. Sumiller Bot recibe request
3. Memory MCP recupera historial del usuario
4. RAG MCP expande y mejora la consulta
5. ChromaDB realiza búsqueda semántica
6. IA genera recomendación personalizada
7. Memory MCP guarda la interacción

## 📚 Documentación Adicional

- [Arquitectura MCP](./mcp-agentic-rag/README.md)
- [API Reference](./docs/api.md)
- [Despliegue Cloud](./README.md#cloud-deployment) 