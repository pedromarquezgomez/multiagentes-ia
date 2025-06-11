# 🍷 Setup - Sistema Sumiller con IA

## Prerrequisitos

1. **Docker y Docker Compose** instalados
2. **Cuenta de OpenAI** con API key activa
3. **Git** (opcional, para clonar el proyecto)

## Instalación paso a paso

### 1. Configurar API Key de OpenAI

```bash
# En la raíz del proyecto, crear archivo .env
cp .env.example .env

# Editar .env y poner tu API key
# OPENAI_API_KEY=sk-tu-api-key-aqui
```

### 2. Crear estructura del MCP Server

```bash
# Crear directorio para MCP Server
mkdir -p mcp-server

# Crear los archivos necesarios
# Copiar el contenido de los artifacts:
# - mcp-server/main.py
# - mcp-server/requirements.txt
# - mcp-server/Dockerfile
```

### 3. Actualizar archivos existentes

```bash
# Reemplazar el contenido de:
# - sumiller-bot/main.py (con la versión actualizada)
# - sumiller-bot/requirements.txt (con las nuevas dependencias)
# - sumiller-bot/Dockerfile (con las librerías de sistema)
# - docker-compose.yaml (con la versión que incluye MCP)
```

### 4. Construir y ejecutar

```bash
# Construir todas las imágenes
docker compose build

# Ejecutar el sistema completo
docker compose up
```

## 🔍 Verificar que funciona

### 1. Verificar servicios

Todos los servicios deben estar corriendo:
- UI: http://localhost:3000
- Maitre Bot: http://localhost:8000
- Sumiller Bot: http://localhost:8001
- MCP Server: http://localhost:8002

### 2. Verificar ChromaDB

```bash
# Ver el conocimiento cargado
curl http://localhost:8001/knowledge/wines
```

### 3. Verificar MCP Server

```bash
# Ver herramientas disponibles
curl http://localhost:8002/tools

# Ver inventario
curl http://localhost:8002/inventory
```

### 4. Probar una consulta

En la UI (http://localhost:3000), prueba con:
- "¿Qué vino recomiendas para una paella?"
- "Necesito un vino tinto para carne asada"
- "¿Qué espumoso tienes disponible?"

## 🎯 Características implementadas

1. **RAG con ChromaDB**: Base vectorial con 10 vinos españoles precargados
2. **OpenAI Integration**: Embeddings y generación de respuestas con GPT-4
3. **MCP Server completo**: 
   - Búsqueda en inventario
   - Verificación de stock
   - Cálculo de maridajes
   - Detalles de vinos
4. **Gestión segura de API keys**: Usando variables de entorno

## 🛠️ Solución de problemas

### Error: "OPENAI_API_KEY no configurada"
- Verificar que el archivo `.env` existe y contiene la API key
- Reiniciar los contenedores: `docker compose down && docker compose up`

### Error de ChromaDB
- El volumen puede estar corrupto: `docker volume rm multiagent-restaurant_chromadb_data`
- Reconstruir: `docker compose up --build`

### Error de conexión entre servicios
- Verificar que todos los servicios están en la misma red
- Revisar logs: `docker compose logs [servicio]`

## 📚 Extender el sistema

### Agregar más vinos
```bash
curl -X POST http://localhost:8001/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{
    "wine_id": "rioja_001",
    "content": "Rioja Gran Reserva: Tinto con largo envejecimiento...",
    "metadata": {"type": "red", "region": "Rioja", "price": "35-60€"}
  }'
```

### Conectar con inventario real
Modificar `mcp-server/main.py` para conectar con:
- Base de datos real
- API de bodega
- Sistema ERP

### Agregar más herramientas MCP
En `available_tools` del MCP Server, agregar nuevas herramientas siguiendo el patrón existente.