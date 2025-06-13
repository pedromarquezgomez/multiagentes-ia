# ✅ Comandos Corregidos para Railway

## 🔧 Sintaxis Correcta

### ❌ **INCORRECTO** (lo que estaba en los archivos anteriores):
```bash
railway variables set OPENAI_API_KEY="tu-key"
```

### ✅ **CORRECTO** (sintaxis actualizada):
```bash
railway variables --set "OPENAI_API_KEY=tu-key"
```

## 🚀 Secuencia Completa de Despliegue

### 1. **Instalar Railway CLI**
```bash
npm install -g @railway/cli
```

### 2. **Login en Railway**
```bash
railway login
```

### 3. **Crear/Conectar Proyecto**
```bash
# Opción A: Crear nuevo proyecto
railway init

# Opción B: Conectar proyecto existente
railway link
```

### 4. **Configurar Variables de Entorno**
```bash
# Configurar tu API Key de OpenAI
railway variables --set "OPENAI_API_KEY=sk-tu-api-key-real-aquí"

# Configurar URL base de OpenAI
railway variables --set "OPENAI_BASE_URL=https://api.openai.com/v1"

# Configurar modelo a usar
railway variables --set "OPENAI_MODEL=gpt-4o-mini"

# Configurar entorno
railway variables --set "ENVIRONMENT=production"
```

### 5. **Verificar Variables**
```bash
railway variables
```

### 6. **Desplegar**
```bash
railway up
```

### 7. **Ver Logs**
```bash
railway logs --follow
```

## 🔑 Variables Críticas Requeridas

```bash
OPENAI_API_KEY=sk-tu-api-key-real
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
ENVIRONMENT=production
```

## 🎯 Comandos Útiles Post-Despliegue

```bash
# Ver estado de servicios
railway status

# Ver servicios activos
railway ps

# Reiniciar servicio
railway restart

# Abrir app en navegador
railway open

# Ver dominio asignado
railway domain

# Conectar a shell del servicio
railway shell
```

## 🐛 Troubleshooting

### Si aparece "No service linked":
```bash
railway service
# O crear nuevo servicio:
railway service new
```

### Si el despliegue falla:
```bash
# Ver logs detallados
railway logs --tail 100

# Verificar variables
railway variables

# Ver status
railway status
```

## 📝 Notas Importantes

1. **API Key**: Asegúrate de usar tu API key real de OpenAI
2. **Sintaxis**: Siempre usar `--set "KEY=value"` (no `set KEY="value"`)
3. **Comillas**: Usar comillas dobles alrededor de todo el par `key=value`
4. **Servicio**: Debes estar vinculado a un servicio para configurar variables

---

🎉 **¡Los comandos ahora están corregidos y funcionarán correctamente!** 