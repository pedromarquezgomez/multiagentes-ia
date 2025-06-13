# 🚂 Configuración Railway - Sistema Sumiller Multi-Agente

## 📋 Servicios Requeridos

Necesitas crear **3 servicios** en Railway + **Firebase** para UI:

### 1. 🗄️ **Redis Database**
```bash
# En Railway Dashboard:
1. Añadir servicio → Database → Redis
2. Nombrar: "redis-sumiller"
3. Copiar REDIS_URL del dashboard
```

### 2. 🔍 **RAG MCP Server**
```bash
# Configuración del servicio:
- Nombre: "rag-mcp-server"
- Archivo: railway.rag.json
- Dockerfile: mcp-agentic-rag/Dockerfile.railway-rag

# Variables de entorno:
ENVIRONMENT=railway
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
VECTOR_DB_TYPE=chroma
```

### 3. 🧠 **Memory MCP Server**
```bash
# Configuración del servicio:
- Nombre: "memory-mcp-server"  
- Archivo: railway.memory.json
- Dockerfile: mcp-agentic-rag/Dockerfile.railway-memory

# Variables de entorno:
ENVIRONMENT=railway
REDIS_URL=${{redis-sumiller.REDIS_URL}} # Referencia automática
```

### 4. 🤖 **Sumiller Bot (Principal)**
```bash
# Configuración del servicio:
- Nombre: "sumiller-bot"
- Archivo: railway.json (por defecto)
- Dockerfile: sumiller-bot/Dockerfile.railway

# Variables de entorno:
ENVIRONMENT=railway
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
RAG_MCP_URL=${{rag-mcp-server.RAILWAY_PUBLIC_DOMAIN}}
MEMORY_MCP_URL=${{memory-mcp-server.RAILWAY_PUBLIC_DOMAIN}}
```

### 5. 🎨 **UI Frontend (Firebase)**
```bash
# Se despliega en Firebase, NO en Railway
# Ver sección de Firebase deployment

# Variables de entorno locales:
VITE_API_URL=https://sumiller-bot-xxxxx.railway.app
```

## 📋 Checklist de Deployment

### ✅ Paso 1: Preparar el Repositorio
```bash
# 1. Commit todos los archivos de configuración
git add railway*.json
git add multiagent-restaurant/mcp-agentic-rag/Dockerfile.railway-*
git add multiagent-restaurant/sumiller-bot/Dockerfile.railway
git commit -m "Añadir configuraciones Railway"
git push
```

### ✅ Paso 2: Crear Servicios en Railway
```bash
# Orden de creación (importante):
1. Redis Database
2. RAG MCP Server 
3. Memory MCP Server
4. Sumiller Bot
```

### ✅ Paso 3: Desplegar UI en Firebase
```bash
# 1. Configurar proyecto Firebase
cd ui
firebase init

# 2. Configurar variables de entorno
# Crear archivo .env en /ui con:
VITE_API_URL=https://sumiller-bot-xxxxx.railway.app

# 3. Build y deploy
npm run build
firebase deploy
```

### ✅ Paso 4: Configurar Variables de Entorno

#### 🗄️ Redis (Ya configurado automáticamente)
- No requiere configuración manual

#### 🔍 RAG MCP Server
```bash
ENVIRONMENT=railway
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
VECTOR_DB_TYPE=chroma
```

#### 🧠 Memory MCP Server  
```bash
ENVIRONMENT=railway
REDIS_URL=${{redis-sumiller.REDIS_URL}}
```

#### 🤖 Sumiller Bot
```bash
ENVIRONMENT=railway
OPENAI_API_KEY=sk-xxxxxxxxxxxxx  
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
RAG_MCP_URL=https://${{rag-mcp-server.RAILWAY_PUBLIC_DOMAIN}}
MEMORY_MCP_URL=https://${{memory-mcp-server.RAILWAY_PUBLIC_DOMAIN}}
HTTP_POOL_MAX_CONNECTIONS=100
CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
```

## 🚀 Comandos Railway CLI

### Desplegar servicios individualmente:
```bash
# RAG MCP Server
railway up --service rag-mcp-server --config railway.rag.json

# Memory MCP Server  
railway up --service memory-mcp-server --config railway.memory.json

# Sumiller Bot
railway up --service sumiller-bot --config railway.json

# UI Frontend
railway up --service sumiller-ui --config railway.ui.json
```

## 🔗 URLs del Sistema

Después del deployment, tendrás:

```bash
# Servicios Backend
https://rag-mcp-server-xxxxx.railway.app/health
https://memory-mcp-server-xxxxx.railway.app/health  
https://sumiller-bot-xxxxx.railway.app/health

# Frontend
https://sumiller-ui-xxxxx.railway.app

# API Principal
https://sumiller-bot-xxxxx.railway.app/query
```

## 🧪 Testing Post-Deployment

```bash
# Test RAG MCP Server
curl https://rag-mcp-server-xxxxx.railway.app/search?q=tempranillo

# Test Memory MCP Server
curl https://memory-mcp-server-xxxxx.railway.app/health

# Test Sumiller Bot
curl -X POST https://sumiller-bot-xxxxx.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino recomiendas para una paella?", "user_id": "test_user"}'
```

## 🔧 Troubleshooting

### ❌ Error: "Cannot connect to Redis"
```bash
# Verificar REDIS_URL en Memory MCP Server
# Debe ser: redis://default:password@host:port
```

### ❌ Error: "RAG MCP Server unreachable"  
```bash
# Verificar que RAG_MCP_URL tenga https://
# Verificar que el servicio RAG esté running
```

### ❌ Error: "OpenAI API key invalid"
```bash
# Verificar OPENAI_API_KEY en todos los servicios
# Debe empezar con sk-
```

## 📊 Monitoreo

### Health Checks disponibles:
- `/health` - Todos los servicios backend
- `/stats` - RAG MCP Server  
- `/` - UI Frontend

### Logs útiles:
```bash
railway logs --service sumiller-bot
railway logs --service rag-mcp-server
railway logs --service memory-mcp-server
``` 