#!/bin/bash
# 🚂 Setup Railway CLI y Redeploy

echo "🚂 Configurando Railway CLI..."

# Verificar si Node.js está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm no está instalado"
    echo "   Instala Node.js desde: https://nodejs.org/"
    exit 1
fi

# Instalar Railway CLI
echo "📦 Instalando Railway CLI..."
npm install -g @railway/cli

# Verificar instalación
if command -v railway &> /dev/null; then
    echo "✅ Railway CLI instalado correctamente"
    railway --version
else
    echo "❌ Error en la instalación de Railway CLI"
    exit 1
fi

echo ""
echo "🔗 Próximos pasos:"
echo "1. railway login"
echo "2. railway link (para conectar al proyecto existente)"
echo "3. railway up (para redesplegar)"

echo ""
echo "🔧 O ejecuta el redeploy directo:"
echo "   ./railway-redeploy.sh" 