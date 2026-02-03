"""
Gestión de historial usando Firebase Firestore.
Reemplaza el almacenamiento en JSON local.
"""

from datetime import datetime
from typing import Optional
import hashlib

from firebase_config import get_firestore_client, is_firestore_available

# Colección principal
COLLECTION_NAME = "businesses"


def _generate_id(url: str) -> str:
    """Genera un ID único basado en la URL."""
    return hashlib.md5(url.encode()).hexdigest()[:16]


def add_analysis(business_data: dict) -> dict:
    """
    Agrega un nuevo análisis al historial en Firestore.
    Si el negocio ya existe (misma URL), lo actualiza.
    """
    db = get_firestore_client()
    
    if db is None:
        # Fallback: retornar datos sin guardar
        business_data["_saved"] = False
        return business_data
    
    # Generar ID único basado en URL
    doc_id = _generate_id(business_data.get("url", ""))
    
    # Agregar timestamp
    business_data["analyzed_at"] = datetime.now().isoformat()
    business_data["_id"] = doc_id
    
    # Guardar en Firestore
    db.collection(COLLECTION_NAME).document(doc_id).set(business_data)
    business_data["_saved"] = True
    
    return business_data


def get_all_analyses() -> list:
    """Obtiene todos los análisis del historial."""
    db = get_firestore_client()
    
    if db is None:
        return []
    
    docs = db.collection(COLLECTION_NAME).stream()
    return [doc.to_dict() for doc in docs]


def get_analyses_by_category(category_id: str) -> list:
    """Obtiene análisis filtrados por categoría."""
    db = get_firestore_client()
    
    if db is None:
        return []
    
    docs = db.collection(COLLECTION_NAME)\
             .where("category.category_id", "==", category_id)\
             .stream()
    
    return [doc.to_dict() for doc in docs]


def get_analysis_by_url(url: str) -> Optional[dict]:
    """Obtiene un análisis específico por URL."""
    db = get_firestore_client()
    
    if db is None:
        return None
    
    doc_id = _generate_id(url)
    doc = db.collection(COLLECTION_NAME).document(doc_id).get()
    
    if doc.exists:
        return doc.to_dict()
    return None


def get_category_stats() -> dict:
    """
    Obtiene estadísticas agregadas por categoría.
    """
    all_analyses = get_all_analyses()
    
    stats = {}
    for business in all_analyses:
        cat_id = business.get("category", {}).get("category_id", "otros")
        cat_name = business.get("category", {}).get("category_name", "Otros")
        cat_icon = business.get("category", {}).get("icon", "📍")
        
        if cat_id not in stats:
            stats[cat_id] = {
                "category_id": cat_id,
                "category_name": cat_name,
                "icon": cat_icon,
                "total_businesses": 0,
                "total_reviews": 0,
                "sentiment_totals": {"positive": 0, "neutral": 0, "negative": 0},
                "bot_totals": {"real": 0, "suspicious": 0, "bot": 0}
            }
        
        stats[cat_id]["total_businesses"] += 1
        stats[cat_id]["total_reviews"] += business.get("total_reviews", 0)
        
        sentiment = business.get("sentiment_summary", {})
        stats[cat_id]["sentiment_totals"]["positive"] += sentiment.get("positive", 0)
        stats[cat_id]["sentiment_totals"]["neutral"] += sentiment.get("neutral", 0)
        stats[cat_id]["sentiment_totals"]["negative"] += sentiment.get("negative", 0)
        
        bot_stats = business.get("bot_stats", {})
        stats[cat_id]["bot_totals"]["real"] += bot_stats.get("real", 0)
        stats[cat_id]["bot_totals"]["suspicious"] += bot_stats.get("suspicious", 0)
        stats[cat_id]["bot_totals"]["bot"] += bot_stats.get("bot", 0)
    
    return stats


def delete_analysis(url: str) -> bool:
    """Elimina un análisis por URL."""
    db = get_firestore_client()
    
    if db is None:
        return False
    
    doc_id = _generate_id(url)
    db.collection(COLLECTION_NAME).document(doc_id).delete()
    return True


def clear_history() -> bool:
    """Limpia todo el historial (usar con cuidado)."""
    db = get_firestore_client()
    
    if db is None:
        return False
    
    docs = db.collection(COLLECTION_NAME).stream()
    for doc in docs:
        doc.reference.delete()
    
    return True
