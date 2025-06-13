#!/bin/bash
# 🚂 Redeploy Railway después de correcciones

set -e

echo "🚂 Redesplegando en Railway tras correcciones..."

# Verificar que Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Error: Railway CLI no está instalado"
    echo "   Ejecuta: ./setup-railway.sh"
    exit 1
fi

# Verificar que estamos logueados
if ! railway whoami &> /dev/null; then
    echo "🔐 No estás logueado en Railway"
    echo "   Ejecutando login..."
    railway login
fi

# Hacer commit de los cambios del Dockerfile
echo "📝 Committing correcciones del Dockerfile..."
git add sumiller-bot/Dockerfile.railway
git commit -m "Fix: Corregir rutas en Dockerfile.railway para Railway build context" || echo "No changes to commit"

# Conectar al proyecto existente si no está linkeado
if ! railway status &> /dev/null; then
    echo "🔗 Conectando al proyecto Railway..."
    echo "   Selecciona tu proyecto 'multiagentes-ia' de la lista:"
    railway link
fi

echo ""
echo "🚀 Redespliegando el proyecto..."

# Redeploy
if railway up; then
    echo ""
    echo "✅ ¡Redeploy exitoso!"
    echo ""
    
    # Mostrar información del deployment
    echo "📊 Estado del deployment:"
    railway status
    
    echo ""
    echo "🔗 URLs del servicio:"
    railway domain
    
    echo ""
    echo "📋 Para ver logs en tiempo real:"
    echo "   railway logs --tail"
    
else
    echo ""
    echo "❌ Error en el redeploy"
    echo ""
    echo "🔍 Ver logs del error:"
    echo "   railway logs --tail"
    echo ""
    echo "🔧 Comandos útiles para debugging:"
    echo "   railway status    # Ver estado"
    echo "   railway logs      # Ver logs completos"
    echo "   railway variables # Ver variables de entorno"
fi

echo ""
echo "🧪 Test del servicio desplegado:"
echo "   curl \$(railway domain)/health" 