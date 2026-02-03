"""
Backend FastAPI para el sistema de análisis de sentimientos.
Soporta clasificación de rubros y almacenamiento de historial.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx

from mock_data import get_mock_data, get_mock_business_analysis
from categories import classify_business, get_all_categories

# Usar Firestore para persistencia en la nube
# Fallback a history local si Firestore no está configurado
try:
    from history_firestore import (
        add_analysis, 
        get_all_analyses, 
        get_analyses_by_category,
        get_category_stats,
        clear_history
    )
    print("📦 Usando Firestore para historial")
except ImportError:
    from history import (
        add_analysis, 
        get_all_analyses, 
        get_analyses_by_category,
        get_category_stats,
        clear_history
    )
    print("📦 Usando JSON local para historial")

app = FastAPI(
    title="Sentiment Analysis API",
    description="API para análisis de sentimientos con clasificación de rubros",
    version="2.0.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Modelo para solicitud de análisis."""
    url: str
    business_name: Optional[str] = None


# ============== ENDPOINTS ==============

@app.get("/")
async def root():
    """Información de la API."""
    return {
        "message": "API de Análisis de Sentimientos v2.0",
        "features": ["Clasificación de rubros", "Historial persistente", "Detección de bots"],
        "endpoints": {
            "/analyze": "POST - Analizar URL de Google Maps",
            "/history": "GET - Obtener historial completo",
            "/history/category/{id}": "GET - Historial por rubro",
            "/categories": "GET - Lista de rubros disponibles",
            "/stats": "GET - Estadísticas por rubro"
        }
    }


@app.get("/categories")
async def list_categories():
    """Retorna todas las categorías disponibles."""
    return get_all_categories()


@app.post("/analyze")
async def analyze_url(request: AnalyzeRequest):
    """
    Analiza una URL de Google Maps.
    Llama a la API del compañero, clasifica el rubro y guarda en historial.
    """
    # URL de la API del compañero (ya desplegada en Render)
    COMPANION_API_URL = "https://modelscrappy.onrender.com/analyze"
    
    try:
        print(f"🔄 Llamando API del compañero con URL: {request.url}")
        
        # Llamar a la API del compañero (timeout alto porque puede tardar)
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                COMPANION_API_URL,
                json={
                    "maps_url": request.url,
                    "forceUpdate": False,
                    "limit": 50
                }
            )
            
            print(f"📡 Respuesta del compañero: {response.status_code}")
            
            # Si hay error HTTP, mostrar el body del error
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ Error del compañero: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"API del modelo respondió con error: {error_detail[:500]}"
                )
            
            companion_data = response.json()
            print(f"✅ Datos recibidos: {len(companion_data.get('reviews', []))} reseñas")
        
        # Mapear respuesta del compañero a nuestro formato
        analysis_data = transform_companion_response(companion_data, request.url)
        
    except httpx.TimeoutException:
        print("⏱️ Timeout llamando API del compañero")
        raise HTTPException(status_code=504, detail="La API del modelo tardó demasiado (>180s). Intenta de nuevo.")
    except httpx.RequestError as e:
        print(f"🔌 Error de conexión: {e}")
        raise HTTPException(status_code=502, detail=f"Error de conexión con la API: {str(e)}")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando la respuesta: {str(e)}")
    
    # Clasificar rubro automáticamente
    business_name = analysis_data.get("name", "")
    category = classify_business(business_name, request.url)
    analysis_data["category"] = category
    analysis_data["url"] = request.url
    
    # Guardar en historial
    saved = add_analysis(analysis_data)
    
    return saved


@app.get("/history")
async def get_history():
    """Obtiene todo el historial de análisis."""
    return {
        "businesses": get_all_analyses(),
        "total": len(get_all_analyses())
    }


@app.get("/history/category/{category_id}")
async def get_history_by_category(category_id: str):
    """Obtiene historial filtrado por categoría."""
    businesses = get_analyses_by_category(category_id)
    return {
        "category_id": category_id,
        "businesses": businesses,
        "total": len(businesses)
    }


@app.get("/stats")
async def get_stats():
    """Obtiene estadísticas agregadas por categoría."""
    return get_category_stats()


@app.delete("/history")
async def delete_history():
    """Limpia todo el historial."""
    success = clear_history()
    if success:
        return {"message": "Historial eliminado correctamente"}
    raise HTTPException(status_code=500, detail="Error al eliminar historial")


@app.get("/mock-analysis")
async def get_mock_analysis():
    """Retorna datos simulados (para desarrollo)."""
    return get_mock_data()


@app.get("/health")
async def health_check():
    """Verificar que el servidor está funcionando."""
    return {"status": "healthy", "version": "2.0.0"}


# ============== UTILIDADES ==============

def extract_name_from_url(url: str) -> str:
    """Extrae un nombre aproximado de la URL de Google Maps."""
    # Intentar extraer de patterns comunes de Google Maps
    if "place/" in url:
        parts = url.split("place/")
        if len(parts) > 1:
            name = parts[1].split("/")[0].replace("+", " ").replace("%20", " ")
            return name
    return "Negocio sin nombre"


def transform_companion_response(data: dict, url: str) -> dict:
    """
    Transforma la respuesta de la API del compañero a nuestro formato.
    Mapea POS/NEG/NEU a positive/negative/neutral y calcula bot scores.
    """
    try:
        # Mapeo de sentimientos
        sentiment_map = {"POS": "positive", "NEG": "negative", "NEU": "neutral"}
        
        # Transformar cada reseña
        transformed_reviews = []
        for review in data.get("reviews", []):
            sentiment_code = review.get("sentiment", "NEU")
            confidence = review.get("confidence", 0.5)
            
            # Calcular bot score basado en patrones
            bot_score = calculate_bot_score(review)
            bot_classification = "real" if bot_score <= 30 else ("suspicious" if bot_score <= 60 else "bot")
            
            # Rating puede venir como float, convertir a int
            rating = review.get("rating", 3)
            if isinstance(rating, float):
                rating = int(rating)
            
            transformed_reviews.append({
                "author": review.get("username", "Anónimo"),
                "text": review.get("review_text", ""),
                "rating": rating,
                "sentiment": sentiment_map.get(sentiment_code, "neutral"),
                "confidence": float(confidence) if confidence else 0.5,
                "bot_score": bot_score,
                "bot_classification": bot_classification,
                "bot_indicators": get_bot_indicators(review)
            })
        
        # Mapear sentiment_summary
        raw_summary = data.get("sentiment_summary", {})
        sentiment_summary = {
            "positive": raw_summary.get("POS", 0),
            "neutral": raw_summary.get("NEU", 0),
            "negative": raw_summary.get("NEG", 0)
        }
        
        # Calcular estadísticas de bots
        real_count = sum(1 for r in transformed_reviews if r["bot_classification"] == "real")
        suspicious_count = sum(1 for r in transformed_reviews if r["bot_classification"] == "suspicious")
        bot_count = sum(1 for r in transformed_reviews if r["bot_classification"] == "bot")
        
        result = {
            "name": data.get("business_name", "Negocio"),
            "url": url,
            "total_reviews": data.get("total_reviews", len(transformed_reviews)),
            "average_rating": data.get("average_rating", 0),
            "sentiment_summary": sentiment_summary,
            "bot_stats": {
                "real": real_count,
                "suspicious": suspicious_count,
                "bot": bot_count
            },
            "reviews": transformed_reviews
        }
        
        print(f"🔄 Transformación completada: {len(transformed_reviews)} reseñas procesadas")
        return result
        
    except Exception as e:
        print(f"❌ Error en transformación: {e}")
        import traceback
        traceback.print_exc()
        raise


def calculate_bot_score(review: dict) -> int:
    """Calcula un puntaje de probabilidad de bot (0-100)."""
    score = 0
    text = review.get("review_text", "")
    
    # Texto muy corto (+20)
    if len(text) < 20:
        score += 25
    
    # Frases genéricas (+25)
    generic_phrases = ["excelente", "muy bueno", "recomendado", "bueno", "ok", "malo"]
    if text.lower().strip() in generic_phrases or len(text.split()) <= 3:
        score += 25
    
    # Rating extremo sin justificación (+15)
    rating = review.get("rating", 3)
    if rating in [1, 5] and len(text) < 50:
        score += 15
    
    # Baja confianza del modelo NLP (+20)
    confidence = review.get("confidence", 1.0)
    if confidence < 0.6:
        score += 20
    
    return min(score, 100)


def get_bot_indicators(review: dict) -> list:
    """Retorna lista de indicadores de bot detectados."""
    indicators = []
    text = review.get("review_text", "")
    
    if len(text) < 20:
        indicators.append("short_text")
    
    if len(text.split()) <= 3:
        indicators.append("generic_phrases")
    
    if review.get("confidence", 1.0) < 0.6:
        indicators.append("low_confidence")
    
    rating = review.get("rating", 3)
    if rating in [1, 5] and len(text) < 50:
        indicators.append("extreme_rating")
    
    return indicators


# ============== PARA CORRER ==============
# uvicorn main:app --reload --port 8000

