# 🍷 Sistema Sumiller Virtual con RAG Agéntico

Sistema inteligente de recomendación de vinos que utiliza **DeepSeek** y **MCP Agentic RAG** para proporcionar recomendaciones personalizadas y conversacionales.

## 🏗️ Arquitectura Real Actual

```
┌─────────────┐    HTTP     ┌─────────────────┐    MCP     ┌──────────────────┐
│     UI      │────────────▶│  Sumiller Bot   │───────────▶│  RAG MCP Server  │
│   (Vue.js)  │◀────────────│   (DeepSeek)    │◀───────────│  (Búsqueda +     │
└─────────────┘             └─────────────────┘            │   Generación)    │
                                     │                     └──────────────────┘
                                     │ MCP                            │
                                     ▼                                ▼
                            ┌─────────────────┐              ┌──────────────────┐
                            │ Memory MCP      │              │    ChromaDB      │
                            │    Server       │              │ (Base Vectorial) │
                            └─────────────────┘              └──────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │     Redis       │
                            │   (Memoria)     │
                            └─────────────────┘
```

## 📁 Estructura del Proyecto

```
multiagent-restaurant/
├── sumiller-bot/           # ÚNICO BOT - Agente principal con DeepSeek
│   ├── main.py            # API FastAPI con integración MCP
│   ├── config.py          # Configuración DeepSeek
│   └── Dockerfile         
├── mcp-agentic-rag/       # Sistema MCP de RAG Agéntico
│   ├── rag_mcp_server.py  # Servidor de búsqueda semántica
│   ├── memory_mcp_server.py # Servidor de memoria conversacional
│   └── knowledge_base/    # Base de conocimientos de vinos
├── ui/                    # Frontend Vue.js
│   ├── src/App.vue        # Interfaz principal
│   └── Dockerfile         
├── docker-compose.yaml    # Orquestación completa
├── env.example           # Variables de entorno
└── config.py             # Configuración global
```

## 🚀 Inicio Rápido

### 1. **Configuración**

```bash
# Clonar y preparar
git clone <repository>
cd multiagent-restaurant

# Configurar variables de entorno
cp env.example .env
# Editar .env y agregar tu DEEPSEEK_API_KEY
```

### 2. **Ejecutar Localmente**

```bash
# Construir y ejecutar todos los servicios
docker compose up --build

# Servicios disponibles:
# - UI: http://localhost:3000
# - Sumiller Bot: http://localhost:8001
# - RAG MCP Server: http://localhost:8000
# - Memory MCP Server: http://localhost:8002
# - Tester: http://localhost:8003
```

### 3. **Cargar Datos de Vinos**

```bash
# Cargar la base de conocimientos
python load-wines.py

# Verificar carga
curl http://localhost:8000/stats
```

## 🔧 Configuración DeepSeek

### Obtener API Key
1. Registrarse en [DeepSeek Platform](https://platform.deepseek.com/)
2. Crear una API Key
3. Configurar en `.env`:

```bash
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 🌐 Despliegue en Producción

### Firebase + Google Cloud Run

```bash
# 1. Configurar proyecto GCP
export PROJECT_ID=tu-proyecto-id
gcloud config set project $PROJECT_ID

# 2. Desplegar servicios backend
./deploy.sh

# 3. Desplegar UI a Firebase
cd ui
firebase deploy
```

### URLs de Producción
- **Frontend**: https://maitre-ia.web.app
- **Backend**: https://sumiller-bot-xxxxx.run.app
- **RAG Server**: https://rag-mcp-server-xxxxx.run.app

## 🧪 Testing y Desarrollo

### Pruebas con cURL

```bash
# Consulta al sumiller
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino recomiendas para una paella?", "user_id": "test_user"}'

# Verificar RAG
curl http://localhost:8000/search?q=tempranillo

# Estado de servicios
curl http://localhost:8001/health
curl http://localhost:8000/health
curl http://localhost:8002/health
```

### Interfaz de Testing
- **Tester Web**: http://localhost:8003
- **Logs**: `docker compose logs -f sumiller-bot`

## 🎯 Características

### 🤖 **Agente Sumiller**
- **DeepSeek LLM** para respuestas naturales
- **RAG Agéntico** con expansión de consultas
- **Memoria conversacional** personalizada
- **Búsqueda semántica** en base de vinos

### 🔍 **RAG Avanzado**
- **Expansión automática** de consultas
- **Búsqueda vectorial** con ChromaDB
- **Deduplicación** inteligente
- **Contexto enriquecido** para mejores respuestas

### 💾 **Memoria Inteligente**
- **Preferencias de usuario** persistentes
- **Historial conversacional** en Redis
- **Personalización** progresiva

### 🎨 **Interfaz Moderna**
- **Vue.js** con diseño responsivo
- **Autenticación Firebase**
- **Chat en tiempo real**
- **Historial de conversaciones**

## 🔧 Configuración Avanzada

### Variables de Entorno Principales

```bash
# API DeepSeek (requerida)
DEEPSEEK_API_KEY=sk-xxxxx

# Entorno
ENVIRONMENT=local  # o 'cloud'

# Puertos locales
SUMILLER_PORT=8001
RAG_MCP_PORT=8000
MEMORY_MCP_PORT=8002

# URLs Cloud Run (producción)
CLOUD_SUMILLER_URL=https://sumiller-bot-xxxxx.run.app
CLOUD_RAG_MCP_URL=https://rag-mcp-server-xxxxx.run.app
```

### Personalización

#### Agregar Nuevos Vinos
```bash
# Editar knowledge_base/wines.json
# Recargar datos
python load-wines.py
```

#### Modificar Personalidad del Sumiller
```python
# En sumiller-bot/main.py, modificar system_prompt
SUMILLER_PERSONALITY = """
Eres Sumy, un sumiller experto con...
"""
```

## 🐛 Troubleshooting

### Problemas Comunes

**❌ "DeepSeek API key not configured"**
```bash
# Verificar .env
cat .env | grep DEEPSEEK_API_KEY
# Debe mostrar tu API key válida
```

**❌ "Error al conectar con RAG MCP Server"**
```bash
# Verificar servicios
docker compose ps
curl http://localhost:8000/health
```

**❌ "No se encontraron vinos"**
```bash
# Recargar base de datos
python load-wines.py
curl http://localhost:8000/stats
```

### Logs Útiles
```bash
# Logs del sumiller
docker compose logs -f sumiller-bot

# Logs del RAG
docker compose logs -f rag-mcp-server

# Logs de memoria
docker compose logs -f memory-mcp-server
```

## 📊 Monitoreo

### Métricas Disponibles
- `/health` - Estado de servicios
- `/stats` - Estadísticas de uso
- Redis insights para memoria
- ChromaDB metrics para RAG

### Health Checks
```bash
# Script de verificación completa
./check-local.sh
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para detalles.

---

**💡 Consejo:** Para mejores resultados, utiliza consultas específicas como "vino tinto para carne asada" en lugar de "recomienda vino".