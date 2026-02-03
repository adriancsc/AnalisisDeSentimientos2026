"""
Configuración de Firebase/Firestore.
Soporta tanto credenciales locales (archivo JSON) como variables de entorno (para Render).
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Variable global para el cliente de Firestore
_db = None


def get_firestore_client():
    """
    Obtiene el cliente de Firestore, inicializándolo si es necesario.
    
    Soporta dos modos:
    1. Variable de entorno FIREBASE_CREDENTIALS_JSON (para Render/producción)
    2. Archivo local firebase-credentials.json (para desarrollo)
    """
    global _db
    
    if _db is not None:
        return _db
    
    try:
        # Opción 1: Credenciales desde variable de entorno (Render)
        creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
        
        if creds_json:
            creds_dict = json.loads(creds_json)
            cred = credentials.Certificate(creds_dict)
        else:
            # Opción 2: Archivo local (desarrollo)
            creds_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
            
            if os.path.exists(creds_path):
                cred = credentials.Certificate(creds_path)
            else:
                print("⚠️ No se encontraron credenciales de Firebase.")
                print("   Para desarrollo: coloca firebase-credentials.json en backend/")
                print("   Para producción: configura FIREBASE_CREDENTIALS_JSON")
                return None
        
        # Inicializar Firebase
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("✅ Firestore conectado exitosamente")
        return _db
        
    except Exception as e:
        print(f"❌ Error conectando a Firestore: {e}")
        return None


def is_firestore_available():
    """Verifica si Firestore está disponible."""
    return get_firestore_client() is not None
