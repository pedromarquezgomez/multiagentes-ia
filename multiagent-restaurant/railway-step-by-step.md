# 🚂 Guía Paso a Paso: Railway desde Cero

## 📋 **Orden de Implementación**

### **PASO 1: Sumiller Bot (Principal)** ⭐
**Prioridad**: CRÍTICA - Es el servicio principal
```bash
Servicio: sumiller-bot
Dockerfile: sumiller-bot/Dockerfile.railway
Variables: ENVIRONMENT, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
```

### **PASO 2: Redis Database** 🗄️
**Prioridad**: ALTA - Necesario para Memory MCP
```bash
Tipo: Database → Redis
Configuración: Automática
Variables: Se genera REDIS_URL automáticamente
```

### **PASO 3: RAG MCP Server** 🔍
**Prioridad**: ALTA - Mejora significativa
```bash
Servicio: rag-mcp-server
Dockerfile: mcp-agentic-rag/Dockerfile.railway-rag
Variables: ENVIRONMENT, OPENAI_*, VECTOR_DB_TYPE
```

### **PASO 4: Memory MCP Server** 🧠
**Prioridad**: MEDIA - Funcionalidad avanzada
```bash
Servicio: memory-mcp-server
Dockerfile: mcp-agentic-rag/Dockerfile.railway-memory
Variables: ENVIRONMENT, REDIS_URL
```

### **PASO 5: Conectar Servicios** 🔗
**Prioridad**: CRÍTICA - Para que funcionen juntos
```bash
Actualizar Sumiller Bot con:
- RAG_MCP_URL
- MEMORY_MCP_URL
```

### **PASO 6: UI Frontend** 🎨
**Prioridad**: BAJA - Interfaz visual
```bash
Plataforma: Firebase
Variables: VITE_API_URL
```

---

## 🎯 **IMPLEMENTACIÓN PASO 1: SUMILLER BOT**

### **A. Crear Servicio en Railway**
1. **Dashboard Railway** → **"New Service"**
2. **Seleccionar**: "GitHub Repo"
3. **Repositorio**: Tu repo multiagentes-ia
4. **Configuración**:
   - **Service Name**: `sumiller-bot`
   - **Root Directory**: `multiagent-restaurant`
   - **Dockerfile Path**: `sumiller-bot/Dockerfile.railway`

### **B. Variables de Entorno**
```bash
ENVIRONMENT=railway
OPENAI_API_KEY=sk-proj-TU_OPENAI_API_KEY_AQUI
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### **C. Deploy y Verificar**
```bash
# Esperar deployment
# Probar: https://sumiller-bot-xxxxx.railway.app/health
```

### **D. Resultado Esperado**
- ✅ Sumiller Bot funcionando básico
- ✅ Respuestas con OpenAI (sin RAG aún)
- ✅ Health check OK

---

## 🗄️ **IMPLEMENTACIÓN PASO 2: REDIS DATABASE**

### **A. Crear Database**
1. **Dashboard Railway** → **"New Service"**
2. **Seleccionar**: "Database" → **"Redis"**
3. **Configuración**: Automática
4. **Nombre**: `redis-memory`

### **B. Verificar Variables**
- Se genera `REDIS_URL` automáticamente
- Formato: `redis://default:password@host:port`

### **C. Resultado Esperado**
- ✅ Redis funcionando
- ✅ REDIS_URL disponible para otros servicios

---

## 🎮 **COMANDOS DE AYUDA**

### **Verificar Estado**
```bash
./verify-deployment.sh          # Verificación completa
railway status                  # Estado Railway
railway logs                   # Ver logs
railway variables              # Ver variables
```

### **Testing Manual**
```bash
# Health check
curl https://SERVICE-URL/health

# Test sumiller
curl -X POST https://SERVICE-URL/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hola", "user_id": "test"}'
```

---

## ⚠️ **IMPORTANTE**

1. **Un servicio a la vez** - No hacer todo junto
2. **Verificar cada paso** antes de continuar
3. **Anotar URLs** de cada servicio
4. **Copiar variables** exactamente como están
5. **Esperar deployment completo** antes del siguiente

---

**🚀 ¿Listo para empezar con el PASO 1 (Sumiller Bot)?** 