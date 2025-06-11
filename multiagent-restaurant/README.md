# Arquitectura Multiagente - Sumiller Virtual

Prototipo mínimo de arquitectura multiagente con comunicación A2A usando FastAPI y estructura MCP simplificada.

## Arquitectura

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│   UI    │────▶│ Maitre Bot  │────▶│ Sumiller Bot │
│  (Vue)  │◀────│(Orquestador)│◀────│ (Experto +   │
└─────────┘     └─────────────┘     │  Mock RAG)   │
                                    └──────────────┘
```

## Estructura del Proyecto

```
.
├── maitre-bot/
│   ├── main.py          # Agente orquestador
│   ├── requirements.txt
│   └── Dockerfile
├── sumiller-bot/
│   ├── main.py          # Agente experto con mock RAG
│   ├── requirements.txt
│   └── Dockerfile
├── ui/
│   ├── src/
│   │   ├── App.vue      # Componente principal Vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yaml
└── README.md
```

## Comunicación A2A con estructura MCP

Los agentes se comunican usando mensajes JSON con estructura MCP simplificada:

```json
{
  "system": "Instrucciones del sistema",
  "user": "Consulta del usuario",
  "context": {
    "key": "value"
  }
}
```

## Ejecución Local

### 1. Con Docker Compose (recomendado)

```bash
# Construir y ejecutar todos los servicios
docker compose up --build

# La UI estará disponible en http://localhost:3000
# Maitre Bot en http://localhost:8000
# Sumiller Bot en http://localhost:8001
```

### 2. Sin Docker (desarrollo)

```bash
# Terminal 1 - Sumiller Bot
cd sumiller-bot
pip install -r requirements.txt
python main.py

# Terminal 2 - Maitre Bot
cd maitre-bot
pip install -r requirements.txt
export SUMILLER_URL=http://localhost:8001
python main.py

# Terminal 3 - UI
cd ui
npm install
npm run dev
```

## Despliegue en Google Cloud Run

### 1. Configurar proyecto

```bash
# Configurar proyecto GCP
export PROJECT_ID=tu-proyecto-id
export REGION=us-central1

gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION
```

### 2. Desplegar Sumiller Bot

```bash
cd sumiller-bot

# Construir y subir imagen
gcloud builds submit --tag gcr.io/$PROJECT_ID/sumiller-bot

# Desplegar en Cloud Run
gcloud run deploy sumiller-bot \
  --image gcr.io/$PROJECT_ID/sumiller-bot \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi
```

### 3. Desplegar Maitre Bot

```bash
cd maitre-bot

# Obtener URL del Sumiller Bot
export SUMILLER_URL=$(gcloud run services describe sumiller-bot --format 'value(status.url)')

# Construir y subir imagen
gcloud builds submit --tag gcr.io/$PROJECT_ID/maitre-bot

# Desplegar con variable de entorno
gcloud run deploy maitre-bot \
  --image gcr.io/$PROJECT_ID/maitre-bot \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars SUMILLER_URL=$SUMILLER_URL
```

### 4. Desplegar UI (opcional)

```bash
cd ui

# Obtener URL del Maitre Bot
export MAITRE_URL=$(gcloud run services describe maitre-bot --format 'value(status.url)')

# Crear archivo .env para producción
echo "VITE_MAITRE_URL=$MAITRE_URL" > .env.production

# Construir y subir imagen
gcloud builds submit --tag gcr.io/$PROJECT_ID/sumiller-ui

# Desplegar
gcloud run deploy sumiller-ui \
  --image gcr.io/$PROJECT_ID/sumiller-ui \
  --platform managed \
  --allow-unauthenticated \
  --memory 256Mi \
  --port 80
```

## Pruebas con cURL

### Consultar al Maitre Bot directamente

```bash
# Local
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino recomiendas para una paella?"}'

# Cloud Run
curl -X POST https://maitre-bot-xxxxx-uc.a.run.app/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "¿Qué vino recomiendas para una paella?"}'
```

### Health checks

```bash
# Maitre Bot
curl http://localhost:8000/

# Sumiller Bot
curl http://localhost:8001/

# Ver platos disponibles
curl http://localhost:8001/knowledge/dishes
```

## Puntos de Extensión

El código incluye comentarios marcando donde se puede extender:

1. **Mock RAG → RAG Real**: En `sumiller-bot/main.py`, función `mock_mcp_query()`
2. **MCP Server Real**: En `sumiller-bot/main.py`, endpoint `/recommend`
3. **Autenticación**: Agregar JWT tokens en headers A2A
4. **Persistencia**: Reemplazar diccionarios en memoria por base de datos
5. **Observabilidad**: Agregar OpenTelemetry para tracing distribuido

## Monitoreo en Cloud Run

```bash
# Ver logs del Maitre Bot
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=maitre-bot" --limit 50

# Ver logs del Sumiller Bot
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sumiller-bot" --limit 50

# Ver métricas
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

## Limpieza

```bash
# Eliminar servicios de Cloud Run
gcloud run services delete maitre-bot --quiet
gcloud run services delete sumiller-bot --quiet
gcloud run services delete sumiller-ui --quiet

# Eliminar imágenes de Container Registry
gcloud container images delete gcr.io/$PROJECT_ID/maitre-bot --quiet
gcloud container images delete gcr.io/$PROJECT_ID/sumiller-bot --quiet
gcloud container images delete gcr.io/$PROJECT_ID/sumiller-ui --quiet
```