# 🚀 Despliegue Rápido en Railway

## ⚡ Resumen Ejecutivo

Este proyecto es un **Sistema Sumiller Virtual con RAG Agéntico** que usa OpenAI y está optimizado para Railway.

## 🎯 Despliegue en 5 Minutos

### 1. **Preparación**
```bash
# Clonar y entrar al directorio
cd multiagent-restaurant

# Hacer ejecutables los scripts
chmod +x railway-commands.sh start-railway.sh
```

### 2. **Usar el Script Interactivo**
```bash
./railway-commands.sh
```

### 3. **Configuración Manual (Alternativa)**
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Conectar proyecto
railway link

# Configurar API Key
railway variables --set "OPENAI_API_KEY=tu-api-key-aquí"
railway variables --set "OPENAI_BASE_URL=https://api.openai.com/v1"
railway variables --set "OPENAI_MODEL=gpt-4o-mini"

# Desplegar
railway up
```

## 🔑 Variables de Entorno Requeridas

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
ENVIRONMENT=production
```

## 📊 Después del Despliegue

### Verificar que funciona:
```bash
# Health check
curl https://tu-dominio.railway.app/health

# Documentación
https://tu-dominio.railway.app/docs
```

### Ver logs:
```bash
railway logs --follow
```

## 🎯 URLs Importantes

Una vez desplegado tendrás acceso a:
- **🌐 Aplicación**: `https://tu-dominio.railway.app`
- **📖 API Docs**: `https://tu-dominio.railway.app/docs`
- **🔍 Health**: `https://tu-dominio.railway.app/health`
- **📊 Stats**: `https://tu-dominio.railway.app/stats`

## 🆘 Ayuda Rápida

### Problemas comunes:
1. **"OpenAI API key not configured"** → Verificar `railway variables`
2. **Error 500** → Revisar `railway logs`
3. **No responde** → Verificar `railway ps`

### Comandos útiles:
```bash
railway status        # Estado general
railway ps           # Servicios activos
railway restart      # Reiniciar
railway variables    # Ver variables
```

## 💰 Costos

- **Gratis**: $5 USD crédito mensual
- **Pro**: $20 USD/mes para producción

---

🎉 **¡Listo!** Tu Sistema Sumiller estará funcionando en Railway. 