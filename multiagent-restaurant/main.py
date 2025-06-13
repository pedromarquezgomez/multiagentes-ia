#!/usr/bin/env python3
"""
Punto de entrada principal para Railway deployment
Ejecuta el sumiller-bot desde su subdirectorio
"""
import os
import sys
import subprocess

def main():
    # Cambiar al directorio del sumiller-bot
    sumiller_dir = os.path.join(os.path.dirname(__file__), 'sumiller-bot')
    os.chdir(sumiller_dir)
    
    # Obtener puerto de Railway
    port = os.getenv("PORT", "8001")
    
    # Ejecutar uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", port,
        "--workers", "1"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 