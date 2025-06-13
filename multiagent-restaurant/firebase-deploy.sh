#!/bin/bash
# 🔥 Script de Deploy Firebase para UI Sumiller

set -e  # Salir si hay algún error

echo "🔥 Desplegando UI Sumiller en Firebase..."

# Verificar que estamos en el directorio correcto
if [ ! -d "ui" ]; then
    echo "❌ Error: No se encontró el directorio ui/"
    echo "   Ejecuta este script desde el directorio multiagent-restaurant"
    exit 1
fi

# Verificar que Firebase CLI está instalado
if ! command -v firebase &> /dev/null; then
    echo "❌ Error: Firebase CLI no está instalado"
    echo "   Instala con: npm install -g firebase-tools"
    exit 1
fi

# Verificar que estamos logueados en Firebase
if ! firebase projects:list &> /dev/null; then
    echo "❌ Error: No estás logueado en Firebase"
    echo "   Ejecuta: firebase login"
    exit 1
fi

echo "✅ Prerequisitos verificados"

# Ir al directorio UI
cd ui

# Solicitar URL del backend Railway si no existe .env
if [ ! -f ".env" ]; then
    echo ""
    echo "🔗 Configuración del Backend"
    read -p "Ingresa la URL de tu Sumiller Bot en Railway (ej: https://sumiller-bot-xxxxx.railway.app): " railway_url
    
    if [ -z "$railway_url" ]; then
        echo "❌ Error: URL del backend es requerida"
        exit 1
    fi
    
    echo "VITE_API_URL=$railway_url" > .env
    echo "✅ Archivo .env creado con: $railway_url"
else
    echo "✅ Usando configuración existente en .env"
    cat .env
fi

# Verificar que las dependencias están instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Build para producción
echo "📦 Building aplicación..."
if npm run build; then
    echo "✅ Build exitoso"
else
    echo "❌ Error en el build"
    exit 1
fi

# Verificar que el directorio dist existe
if [ ! -d "dist" ]; then
    echo "❌ Error: No se generó el directorio dist/"
    exit 1
fi

# Deploy a Firebase
echo "🚀 Desplegando a Firebase..."
if firebase deploy --only hosting; then
    echo "✅ Deploy a Firebase exitoso"
else
    echo "❌ Error en el deploy a Firebase"
    exit 1
fi

# Obtener la URL del sitio desplegado
echo ""
echo "🎉 ¡Deploy completado!"
echo ""

# Mostrar información del proyecto
project_id=$(firebase use --current 2>/dev/null | grep -o '[^ ]*$' || echo "tu-proyecto")
echo "🔗 URLs de tu aplicación:"
echo "   Frontend: https://$project_id.web.app"
echo "   Backend:  $(cat .env | cut -d'=' -f2)"

echo ""
echo "📋 Próximos pasos:"
echo "1. Abrir https://$project_id.web.app"
echo "2. Probar el chat con el sumiller"
echo "3. Verificar que las respuestas llegan correctamente"

echo ""
echo "🧪 Test rápido del backend:"
backend_url=$(cat .env | cut -d'=' -f2)
echo "curl $backend_url/health"

echo ""
echo "✨ ¡Sistema Sumiller desplegado completamente!" 