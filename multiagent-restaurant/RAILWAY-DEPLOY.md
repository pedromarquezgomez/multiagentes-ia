# 🚀 Guía de Despliegue en Railway

Esta guía te llevará paso a paso para desplegar tu Sistema Sumiller Virtual en Railway.

## 📋 Prerrequisitos

1. **Cuenta en Railway**: [Regístrate en Railway](https://railway.app)
2. **API Key de OpenAI**: [Obtén tu API key](https://platform.openai.com/api-keys)
3. **Git**: Tu proyecto debe estar en un repositorio Git

## 🔧 Paso 1: Preparar el Proyecto

### 1.1 Crear repositorio Git (si no lo tienes)
```bash
cd multiagent-restaurant
git init
git add .
git commit -m "Initial commit: Sistema Sumiller"
git remote add origin <tu-repositorio-url>
git push -u origin main
```

## 🚀 Paso 2: Configurar Railway

### 2.1 Conectar con Railway
1. Ve a [Railway Dashboard](https://railway.app/dashboard)
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio

### 2.2 Configurar Servicios
Railway detectará automáticamente el `railway.toml`, pero necesitarás configurar múltiples servicios:

#### **Servicio 1: Sumiller Bot (Principal)**
- **Source**: Tu repositorio
- **Root Directory**: `/multiagent-restaurant`
- **Build Command**: Usa el `Dockerfile.railway`
- **Start Command**: `uvicorn sumiller-bot.main:app --host 0.0.0.0 --port $PORT`

#### **Servicio 2: Redis (Base de Datos)**
- Agrega desde Railway templates: **Redis**
- Railway creará automáticamente las variables `REDIS_URL`

#### **Servicio 3: ChromaDB (Base Vectorial)**
- **Source**: Mismo repositorio
- **Root Directory**: `/multiagent-restaurant/mcp-agentic-rag`
- **Start Command**: `python -m chromadb.cli run --host 0.0.0.0 --port $PORT`

## 🔐 Paso 3: Configurar Variables de Entorno

### 3.1 Variables Principales (OBLIGATORIAS)
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
ENVIRONMENT=production
```

### 3.2 Variables de Conexión (Railway las genera automáticamente)
```bash
# Railway creará estas automáticamente cuando conectes servicios
REDIS_URL=${{Redis.REDIS_URL}}
RAG_MCP_URL=${{RagServer.RAILWAY_PUBLIC_DOMAIN}}
MEMORY_MCP_URL=${{MemoryServer.RAILWAY_PUBLIC_DOMAIN}}
```

### 3.3 Cómo configurar en Railway:
1. Ve a tu proyecto en Railway
2. Selecciona el servicio "Sumiller Bot"
3. Ve a la pestaña "Variables"
4. Agrega cada variable una por una

## 🎯 Paso 4: Estrategia de Despliegue Simplificada

### Opción A: Monolito (Recomendado para empezar)
Despliega todo en un solo servicio para simplificar:

```dockerfile
# Usar el Dockerfile.railway que ya creamos
# Incluye todos los componentes necesarios
```

### Opción B: Microservicios (Avanzado)
- **Servicio 1**: Sumiller Bot
- **Servicio 2**: RAG MCP Server  
- **Servicio 3**: Memory MCP Server
- **Servicio 4**: Redis
- **Servicio 5**: ChromaDB

## 🔨 Paso 5: Comandos de Despliegue

### 5.1 Desde la CLI de Railway
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Conectar proyecto
railway link

# Configurar variables (reemplaza con tu API key)
railway variables --set "OPENAI_API_KEY=tu-api-key-aquí"
railway variables --set "OPENAI_BASE_URL=https://api.openai.com/v1"
railway variables --set "OPENAI_MODEL=gpt-4o-mini"

# Desplegar
railway up
```

### 5.2 Desde el Dashboard
1. Push tu código al repositorio
2. Railway detectará cambios automáticamente
3. Se ejecutará el build y deploy

## 🧪 Paso 6: Verificar el Despliegue

### 6.1 Endpoints de Salud
Una vez desplegado, verifica estos endpoints:
```bash
# Endpoint principal
https://tu-dominio.railway.app/health

# Documentación API
https://tu-dominio.railway.app/docs

# Estado de servicios
https://tu-dominio.railway.app/stats
```

### 6.2 Logs de Servicios
```bash
# Ver logs en tiempo real
railway logs

# Logs de un servicio específico
railway logs --service sumiller-bot
```

## 🐛 Resolución de Problemas

### Problema 1: "OpenAI API key not configured"
```bash
# Verificar variables de entorno
railway variables
```

### Problema 2: "Cannot connect to Redis"
```bash
# Verificar que Redis esté funcionando
railway ps
# Verificar la variable REDIS_URL
```

### Problema 3: "RAG MCP Server not found"
```bash
# Verificar que todos los servicios estén ejecutándose
railway status
```

## 📊 Monitoreo

### Métricas Importantes
- **CPU y Memoria**: Railway dashboard
- **Logs de aplicación**: `railway logs`
- **Health checks**: `/health` endpoint
- **Performance**: Railway Analytics

### Comandos Útiles
```bash
# Ver estado de servicios
railway ps

# Restart servicio
railway restart

# Ver variables
railway variables

# Connect a base de datos
railway connect redis
```

## 💰 Costos Estimados

### Plan Starter (Gratis)
- **$5 USD** de crédito mensual gratis
- Suficiente para desarrollo y pruebas

### Plan Pro ($20/mes)
- **$20 USD** de crédito mensual
- Recomendado para producción

## 🎯 Siguientes Pasos

1. **Dominio Personalizado**: Configura tu propio dominio
2. **SSL Automático**: Railway lo configura automáticamente
3. **CI/CD**: Configura deployments automáticos
4. **Monitoring**: Agrega herramientas de monitoreo
5. **Backups**: Configura respaldos de Redis

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `railway logs`
2. Verifica variables: `railway variables`
3. Consulta [Railway Docs](https://docs.railway.app)
4. Comunidad: [Railway Discord](https://discord.gg/railway) 