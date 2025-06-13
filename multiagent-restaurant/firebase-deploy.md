# 🔥 Guía de Deploy Firebase - UI Sumiller

## 📋 Prerequisitos

1. **Railway Backend** desplegado y funcionando
2. **Firebase CLI** instalado
3. **Proyecto Firebase** configurado

## 🚀 Paso a Paso

### 1. **Instalar Firebase CLI**
```bash
npm install -g firebase-tools
```

### 2. **Login en Firebase**
```bash
firebase login
```

### 3. **Configurar Variables de Entorno**
```bash
cd ui

# Crear archivo .env con la URL de tu Sumiller Bot en Railway
echo "VITE_API_URL=https://sumiller-bot-xxxxx.railway.app" > .env
```

### 4. **Configurar Firebase (si no está configurado)**
```bash
# Inicializar proyecto Firebase
firebase init

# Seleccionar:
# - Hosting: Configure files for Firebase Hosting
# - Use existing project (si ya tienes proyecto) o crear nuevo
# - What do you want to use as your public directory? > dist
# - Configure as a single-page app? > Yes
# - Set up automatic builds and deploys with GitHub? > No (por ahora)
```

### 5. **Build y Deploy**
```bash
# Instalar dependencias
npm install

# Build para producción
npm run build

# Deploy a Firebase
firebase deploy
```

## 🔧 Configuración Automática

### Script de Deploy
```bash
#!/bin/bash
# firebase-deploy.sh

# Variables
RAILWAY_SUMILLER_URL="https://sumiller-bot-xxxxx.railway.app"

echo "🔥 Desplegando UI Sumiller en Firebase..."

# Ir al directorio UI
cd ui

# Configurar variables de entorno
echo "VITE_API_URL=$RAILWAY_SUMILLER_URL" > .env

# Build
echo "📦 Building..."
npm run build

# Deploy
echo "🚀 Deploying..."
firebase deploy

echo "✅ Deploy completado!"
echo "🔗 URL: $(firebase hosting:channel:list | grep live | awk '{print $2}')"
```

### Hacer el script ejecutable
```bash
chmod +x firebase-deploy.sh
./firebase-deploy.sh
```

## 🌐 URLs del Sistema Completo

Después del deploy tendrás:

### 🚂 **Backend (Railway)**
- **RAG MCP**: https://rag-mcp-server-xxxxx.railway.app
- **Memory MCP**: https://memory-mcp-server-xxxxx.railway.app
- **Sumiller Bot**: https://sumiller-bot-xxxxx.railway.app

### 🔥 **Frontend (Firebase)**
- **UI Principal**: https://tu-proyecto.web.app

## 🧪 Testing Post-Deploy

### 1. **Verificar Backend**
```bash
curl https://sumiller-bot-xxxxx.railway.app/health
```

### 2. **Test Consulta Completa**
```bash
curl -X POST https://sumiller-bot-xxxxx.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino recomiendas para una paella?", "user_id": "test_user"}'
```

### 3. **Verificar UI**
- Abrir https://tu-proyecto.web.app
- Probar chat con el sumiller
- Verificar que aparecen respuestas

## 🔧 Troubleshooting

### ❌ **Error: CORS en Firebase**
```bash
# Verificar que la URL del backend sea correcta en .env
# Verificar que el backend tenga CORS configurado para Firebase
```

### ❌ **Error: "API not reachable"**
```bash
# Verificar que el Sumiller Bot esté corriendo
curl https://sumiller-bot-xxxxx.railway.app/health

# Verificar variables de entorno
cat ui/.env
```

### ❌ **Error: Build failed**
```bash
# Limpiar cache y reinstalar
cd ui
rm -rf node_modules dist
npm install
npm run build
```

## 📊 Monitoreo

### Firebase Console
- Métricas de uso en Firebase Console
- Logs de hosting
- Performance monitoring

### Backend Health
```bash
# Health checks automáticos
curl https://sumiller-bot-xxxxx.railway.app/health
curl https://rag-mcp-server-xxxxx.railway.app/health
curl https://memory-mcp-server-xxxxx.railway.app/health
```

## 🚀 Deploy Automatizado Completo

### Script combinado Railway + Firebase
```bash
#!/bin/bash
# deploy-complete.sh

echo "🚀 Deploy completo: Railway + Firebase"

# 1. Deploy backend en Railway
echo "📡 Desplegando backend en Railway..."
./railway-deploy.sh

# 2. Esperar a que los servicios estén listos
echo "⏳ Esperando que los servicios estén listos..."
sleep 30

# 3. Deploy frontend en Firebase
echo "🔥 Desplegando frontend en Firebase..."
./firebase-deploy.sh

echo "🎉 ¡Deploy completo finalizado!" 