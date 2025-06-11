# 🍷 Configuración Multi-Entorno - Sumy Wine Recommender

Este proyecto implementa una **configuración inteligente multi-entorno** que se adapta automáticamente a desarrollo local y Cloud Run sin cambios manuales.

## 🎯 Características

- ✅ **Auto-detección de entorno**: Local vs Cloud Run
- ✅ **URLs dinámicas**: Sin hardcodeo de direcciones
- ✅ **Gestión segura de secrets**: OpenAI API keys
- ✅ **Zero-config deployment**: Un comando para desplegar
- ✅ **Estrategia de chunks con ChromaDB**: Optimización de tokens

## 🚀 Desarrollo Local

### 1. Configuración Inicial

```bash
# Copiar configuración de ejemplo
cp .env.example .env

# Editar con tu API key
nano .env
```

### 2. Iniciar Desarrollo

```bash
# Script automático (recomendado)
./dev.sh

# O manualmente
docker compose up --build
```

### 3. URLs Locales

- 🎩 **Maitre Bot**: http://localhost:8000
- 🍷 **Sumiller Bot**: http://localhost:8001  
- 📚 **MCP Server**: http://localhost:8002
- 🌐 **UI**: http://localhost:3000

## ☁️ Despliegue en Cloud Run

### 1. Configurar Secreto

```bash
# Crear secreto de OpenAI
echo -n 'sk-proj-tu-key' | gcloud secrets create openai-api-key --data-file=-
```

### 2. Desplegar

```bash
# Script automático
./deploy.sh

# O paso a paso
gcloud run deploy mcp-server --source ./mcp-server --region europe-west1
# ... etc
```

## 🔧 Cómo Funciona

### Auto-detección de Entorno

```python
def _detect_environment(self) -> str:
    # Cloud Run tiene estas variables específicas
    if os.getenv('K_SERVICE') or os.getenv('GOOGLE_CLOUD_PROJECT'):
        return 'cloud'
    return 'local'
```

### URLs Dinámicas

#### Local (Docker Compose)
```python
self.maitre_url = f"http://maitre-bot:{self.maitre_port}"
self.sumiller_url = f"http://sumiller-bot:{self.sumiller_port}"
self.mcp_server_url = f"http://mcp-server:{self.mcp_port}"
```

#### Cloud Run
```python
self.maitre_url = os.getenv('CLOUD_MAITRE_URL')
self.sumiller_url = os.getenv('CLOUD_SUMILLER_URL')
self.mcp_server_url = os.getenv('CLOUD_MCP_SERVER_URL')
```

## 📁 Estructura de Configuración

```
multiagent-restaurant/
├── config.py                 # Configuración multi-entorno
├── .env.example              # Plantilla de configuración
├── .env                      # Tu configuración local (no commitear)
├── dev.sh                    # Script desarrollo local
├── deploy.sh                 # Script despliegue Cloud Run
├── docker-compose.yaml       # Configuración local
└── [servicios]/
    ├── maitre-bot/
    ├── sumiller-bot/
    └── mcp-server/
```

## 🔑 Variables de Entorno

### Desarrollo Local (.env)
```bash
ENVIRONMENT=local
OPENAI_API_KEY=sk-proj-tu-key
MAITRE_PORT=8000
SUMILLER_PORT=8001
MCP_SERVER_PORT=8002
```

### Cloud Run (automático)
```bash
ENVIRONMENT=cloud
GOOGLE_CLOUD_PROJECT=tu-proyecto
K_SERVICE=maitre-bot  # (variable automática de Cloud Run)
CLOUD_MAITRE_URL=https://maitre-bot-xyz.a.run.app
CLOUD_SUMILLER_URL=https://sumiller-bot-xyz.a.run.app
CLOUD_MCP_SERVER_URL=https://mcp-server-xyz.a.run.app
```

## 🧪 Testing

### Health Checks
```bash
# Local
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Cloud Run
curl https://maitre-bot-xyz.a.run.app/health
```

### Test Query
```bash
# Local
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un tinto para carne asada"}'

# Cloud Run  
curl -X POST https://maitre-bot-xyz.a.run.app/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Recomiéndame un tinto para carne asada"}'
```

## 🐛 Troubleshooting

### Problema: "No se puede conectar con mcp-server"
```bash
# Verificar que todos los servicios están corriendo
docker compose ps

# Ver logs
docker compose logs mcp-server
```

### Problema: "OpenAI API Key no configurada"
```bash
# Local: verificar .env
cat .env | grep OPENAI_API_KEY

# Cloud Run: verificar secreto
gcloud secrets versions access latest --secret="openai-api-key"
```

### Problema: "Error de configuración"
```bash
# Debugear configuración
python config.py
```

## 📊 Monitoreo

### Logs Locales
```bash
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f sumiller-bot
```

### Logs Cloud Run
```bash
# Ver logs en tiempo real
gcloud logging tail "resource.type=cloud_run_revision"

# Logs específicos
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=sumiller-bot"
```

## 🔄 Workflow Desarrollo → Producción

1. **Desarrollo**: `./dev.sh` → http://localhost:3000
2. **Test local**: Probar todas las funcionalidades
3. **Deploy**: `./deploy.sh` → URLs de Cloud Run
4. **Verificación**: Health checks y tests en producción
5. **Monitoreo**: Logs y métricas

Esta configuración garantiza que el mismo código funcione sin cambios en ambos entornos. 🎉 