# 🍷 Sistema Sumiller Virtual con RAG Agéntico

Sistema inteligente de recomendación de vinos que utiliza **OpenAI GPT-4o-mini** y **MCP Agentic RAG** para proporcionar recomendaciones personalizadas y conversacionales.

## 🏗️ Arquitectura Real Actual

```
┌─────────────┐    HTTPS    ┌─────────────────┐    MCP     ┌──────────────────┐
│     UI      │────────────▶│  Sumiller Bot   │───────────▶│  RAG MCP Server  │
│ (Firebase)  │◀────────────│  (OpenAI GPT)   │◀───────────│  (ChromaDB +     │
└─────────────┘             └─────────────────┘            │   Vectorización) │
     🔥                              🚂                     └──────────────────┘
                                     │                             🚂
                                     │ MCP                         
                                     ▼                         
                            ┌─────────────────┐              
                            │ Memory MCP      │              
                            │    Server       │              
                            └─────────────────┘              
                                     │                       
                                     ▼                       
                            ┌─────────────────┐              
                            │  Railway Redis  │              
                            │   Database      │              
                            └─────────────────┘              
                                     🚂
```

**🚂 Railway Backend** | **🔥 Firebase Frontend**

## 📁 Estructura del Proyecto

```
multiagent-restaurant/
├── sumiller-bot/           # 🤖 Agente principal con OpenAI GPT
│   ├── main.py            # API FastAPI con integración MCP
│   ├── config.py          # Configuración multi-entorno
│   └── Dockerfile.railway # Dockerfile para Railway
├── mcp-agentic-rag/       # 🔍 Sistema MCP de RAG Agéntico
│   ├── rag_mcp_server.py  # Servidor de búsqueda semántica
│   ├── memory_mcp_server.py # Servidor de memoria conversacional
│   ├── knowledge_base/    # Base de conocimientos de vinos
│   └── Dockerfile.railway-* # Dockerfiles para Railway
├── ui/                    # 🎨 Frontend Vue.js
│   ├── src/App.vue        # Interfaz principal
│   └── firebase.json      # Configuración Firebase
├── railway*.json          # Configuraciones Railway
├── *-deploy.sh           # Scripts de deployment
├── verify-deployment.sh   # Script de verificación
├── docker-compose.yaml    # Orquestación local
└── config.py             # Configuración global multi-entorno
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

## 🔧 Configuración OpenAI

### Obtener API Key
1. Registrarse en [OpenAI Platform](https://platform.openai.com/)
2. Crear una API Key
3. Configurar en variables de entorno:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

## 🌐 Despliegue en Producción

### 🚂 Railway (Recomendado) - **CONFIGURACIÓN ACTUAL**

#### **Estado del Deployment:**
- ✅ **Sumiller Bot**: Funcionando completamente
- ⏳ **RAG MCP Server**: Desplegando actualmente  
- ❌ **Memory MCP + Redis**: Pendientes
- ❌ **UI Firebase**: Pendiente

#### **🚀 Deploy Rápido:**
```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login en Railway  
railway login

# 3. Deploy servicios
./railway-deploy.sh        # Deploy backend completo
./firebase-deploy.sh       # Deploy frontend

# 4. Verificar deployment
./verify-deployment.sh
```

#### **📋 URLs Actuales:**
```bash
# ✅ FUNCIONANDO:
curl https://multiagentes-ia-production.up.railway.app/health

# 🧪 Test del Sumiller:
curl -X POST https://multiagentes-ia-production.up.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomienda vino para pasta", "user_id": "test"}'
```

#### **🔧 Configuración Variables (OpenAI):**
```bash
# Variables configuradas en Railway:
ENVIRONMENT=railway
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1  
OPENAI_MODEL=gpt-4o-mini
```

Ver guía completa: `railway-setup.md` | Scripts: `*-deploy.sh`

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

**🚂 Railway (Backend):**
- **✅ Sumiller Bot**: https://multiagentes-ia-production.up.railway.app
- **⏳ RAG MCP**: https://rag-mcp-server-xxxxx.railway.app (desplegando)
- **❌ Memory MCP**: (pendiente)
- **❌ Redis Database**: (pendiente)

**🔥 Firebase (Frontend):**
- **❌ UI Frontend**: (pendiente deployment)

**Google Cloud:**
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
- **OpenAI GPT-4o-mini** para respuestas naturales y rápidas
- **RAG Agéntico** con expansión de consultas
- **Memoria conversacional** personalizada (opcional)
- **Búsqueda semántica** en base de vinos
- **Railway deployment** con auto-scaling

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
# 🚂 RAILWAY PRODUCTION (Actual)
ENVIRONMENT=railway
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 🏠 LOCAL DEVELOPMENT  
ENVIRONMENT=local
SUMILLER_PORT=8001
RAG_MCP_PORT=8000
MEMORY_MCP_PORT=8002

# ☁️ GOOGLE CLOUD (Legacy)
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

**❌ "OpenAI API key not configured"**
```bash
# Verificar variables en Railway
railway variables | grep OPENAI_API_KEY
# O verificar en local
cat .env | grep OPENAI_API_KEY
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

## 🎯 **ESTADO ACTUAL DEL SISTEMA (Railway)**

### ✅ **FUNCIONANDO:**
- **Sumiller Bot API**: https://multiagentes-ia-production.up.railway.app
- **Health Check**: `curl https://multiagentes-ia-production.up.railway.app/health`
- **OpenAI Integration**: GPT-4o-mini configurado y funcionando
- **Basic Wine Recommendations**: Sin base de conocimientos específica

### ⏳ **EN PROCESO:**
- **RAG MCP Server**: Desplegando para búsquedas semánticas
- **Knowledge Base**: Base de datos vectorial de vinos

### ❌ **PENDIENTES:**
- **Memory MCP Server**: Memoria conversacional
- **Redis Database**: Persistencia de conversaciones  
- **UI Frontend**: Interfaz web en Firebase

### 🧪 **TEST RÁPIDO:**
```bash
# Probar el sumiller actual
curl -X POST https://multiagentes-ia-production.up.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino recomiendas para una cena romántica?", "user_id": "test"}'
```

### 📋 **PRÓXIMOS PASOS:**
1. **Completar RAG MCP Server** → Mejor conocimiento de vinos
2. **Desplegar Memory MCP** → Conversaciones personalizadas
3. **Deploy UI Firebase** → Interfaz web completa

---

**💡 Consejo:** Para mejores resultados, utiliza consultas específicas como "vino tinto para carne asada" en lugar de "recomienda vino".