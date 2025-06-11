# maitre-bot/firebase_auth.py
"""
Módulo de autenticación Firebase para el backend
"""
import firebase_admin
from firebase_admin import credentials, auth
import os
import json
import logging

logger = logging.getLogger(__name__)

# Configuración de Firebase Admin
def initialize_firebase():
    """
    Inicializa Firebase Admin SDK
    """
    try:
        # Si ya está inicializado, no hacer nada
        firebase_admin.get_app()
        logger.info("🔥 Firebase ya estaba inicializado")
        return True
    except ValueError:
        # No está inicializado, proceder con la inicialización
        pass
    
    try:
        # Configuración de Firebase (misma que en el frontend)
        firebase_config = {
            "type": "service_account",
            "project_id": "maitre-ia",
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CERT_URL")
        }
        
        # Si no tenemos las variables de entorno, usar certificado por defecto
        if not all([firebase_config.get("private_key_id"), 
                   firebase_config.get("private_key"), 
                   firebase_config.get("client_email")]):
            logger.warning("🚨 Variables de entorno de Firebase no encontradas, usando certificado por defecto")
            # Usar certificado por defecto de aplicación
            cred = credentials.ApplicationDefault()
        else:
            # Usar certificado de servicio
            cred = credentials.Certificate(firebase_config)
        
        firebase_admin.initialize_app(cred)
        logger.info("🔥 Firebase Admin SDK inicializado correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando Firebase: {e}")
        # En desarrollo, continuar sin Firebase
        return False

def verify_firebase_token(id_token: str) -> dict:
    """
    Verifica un token de Firebase y devuelve la información del usuario
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        logger.info(f"✅ Token verificado para usuario: {decoded_token.get('email')}")
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "verified": True
        }
    except Exception as e:
        logger.error(f"❌ Error verificando token: {e}")
        return {"verified": False, "error": str(e)}

def get_user_info(uid: str) -> dict:
    """
    Obtiene información del usuario por UID
    """
    try:
        user = auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "name": user.display_name,
            "photo": user.photo_url,
            "verified": user.email_verified
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuario: {e}")
        return {"error": str(e)} 