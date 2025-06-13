# api/sumiller.py - Punto de entrada para Vercel
import sys
import os

# Agregar el directorio del sumiller-bot al path
sumiller_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sumiller-bot')
sys.path.insert(0, sumiller_path)

# Agregar el directorio raíz al path para config.py
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_path)

# Importar la aplicación FastAPI
from main import app

# Esta es la variable que Vercel buscará
handler = app 