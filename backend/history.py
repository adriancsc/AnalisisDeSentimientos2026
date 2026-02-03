"""
Gestión de historial de análisis.
Almacena y recupera análisis previos en archivo JSON.
"""

import json
import os
from datetime import datetime
from typing import Optional

# Ruta del archivo de historial
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "analysis_history.json")


def load_history() -> dict:
    """Carga el historial desde el archivo JSON."""
    if not os.path.exists(HISTORY_FILE):
        return {"businesses": [], "last_updated": None}
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"businesses": [], "last_updated": None}


def save_history(history: dict) -> bool:
    """Guarda el historial en el archivo JSON."""
    try:
        history["last_updated"] = datetime.now().isoformat()
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def add_analysis(business_data: dict) -> dict:
    """
    Agrega un nuevo análisis al historial.
    Si el negocio ya existe (misma URL), lo actualiza.
    """
    history = load_history()
    
    # Buscar si ya existe
    existing_index = None
    for i, b in enumerate(history["businesses"]):
        if b.get("url") == business_data.get("url"):
            existing_index = i
            break
    
    # Agregar timestamp
    business_data["analyzed_at"] = datetime.now().isoformat()
    
    if existing_index is not None:
        # Actualizar existente
        history["businesses"][existing_index] = business_data
    else:
        # Agregar nuevo
        history["businesses"].append(business_data)
    
    save_history(history)
    return business_data


def get_all_analyses() -> list:
    """Obtiene todos los análisis del historial."""
    history = load_history()
    return history.get("businesses", [])


def get_analyses_by_category(category_id: str) -> list:
    """Obtiene análisis filtrados por categoría."""
    all_analyses = get_all_analyses()
    return [
        b for b in all_analyses 
        if b.get("category", {}).get("category_id") == category_id
    ]


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


def clear_history() -> bool:
    """Limpia todo el historial."""
    try:
        save_history({"businesses": [], "last_updated": None})
        return True
    except:
        return False
