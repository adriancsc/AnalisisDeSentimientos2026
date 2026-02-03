"""
Datos simulados para desarrollo del frontend.
Cuando tu compañero termine la API, reemplaza esto con llamadas reales.
"""

import random
from datetime import datetime

# Datos base para generar análisis mock
SAMPLE_REVIEWS = {
    "positive": [
        {"text": "Excelente atención, muy profesionales. El servicio fue rápido y eficiente.", "rating": 5},
        {"text": "Muy buena experiencia. El personal es amable y las instalaciones están limpias.", "rating": 5},
        {"text": "Recomendado al 100%. Volveré sin duda.", "rating": 5},
        {"text": "Superó mis expectativas. El precio es justo por la calidad.", "rating": 4},
        {"text": "Buen servicio, aunque podría mejorar el tiempo de espera.", "rating": 4},
    ],
    "neutral": [
        {"text": "Regular. Nada especial pero cumple con lo básico.", "rating": 3},
        {"text": "El servicio es aceptable. Hay cosas que mejorar.", "rating": 3},
        {"text": "Instalaciones normales, atención promedio.", "rating": 3},
    ],
    "negative": [
        {"text": "Mala experiencia. Tuve que esperar más de 2 horas.", "rating": 2},
        {"text": "No lo recomiendo. El servicio dejó mucho que desear.", "rating": 1},
        {"text": "Pésima atención. No volveré jamás.", "rating": 1},
    ],
    "bot": [
        {"text": "Excelente", "rating": 5, "bot_score": 80},
        {"text": "Muy bueno", "rating": 5, "bot_score": 75},
        {"text": "Recomendado", "rating": 5, "bot_score": 70},
        {"text": "Bueno", "rating": 4, "bot_score": 65},
    ]
}

SAMPLE_AUTHORS = [
    "María García", "Carlos Mendoza", "Ana López", "José Ramírez",
    "Laura Fernández", "Pedro Sánchez", "Sofía Vargas", "Miguel Torres",
    "Usuario123", "Cliente_2024", "ReviewBot", "User_Test"
]


def generate_reviews(count: int = 10) -> list:
    """Genera reseñas aleatorias."""
    reviews = []
    
    # Distribución: 60% positivas, 20% neutral, 10% negativas, 10% bots
    distribution = {
        "positive": int(count * 0.6),
        "neutral": int(count * 0.2),
        "negative": int(count * 0.1),
        "bot": int(count * 0.1)
    }
    
    for sentiment, num in distribution.items():
        for _ in range(num):
            sample = random.choice(SAMPLE_REVIEWS[sentiment])
            is_bot = sentiment == "bot"
            
            review = {
                "author": random.choice(SAMPLE_AUTHORS),
                "text": sample["text"],
                "rating": sample["rating"],
                "sentiment": "positive" if sentiment in ["positive", "bot"] else sentiment,
                "confidence": round(random.uniform(0.7, 0.98), 2),
                "bot_score": sample.get("bot_score", random.randint(5, 25)),
                "bot_classification": "bot" if is_bot else "real",
                "bot_indicators": ["short_text", "generic_phrases"] if is_bot else []
            }
            reviews.append(review)
    
    return reviews


def get_mock_business_analysis(name: str, url: str) -> dict:
    """Genera análisis mock para un negocio específico."""
    reviews = generate_reviews(random.randint(15, 40))
    
    positive = sum(1 for r in reviews if r["sentiment"] == "positive")
    neutral = sum(1 for r in reviews if r["sentiment"] == "neutral")
    negative = sum(1 for r in reviews if r["sentiment"] == "negative")
    
    real = sum(1 for r in reviews if r["bot_classification"] == "real")
    suspicious = sum(1 for r in reviews if r["bot_classification"] == "suspicious")
    bot = sum(1 for r in reviews if r["bot_classification"] == "bot")
    
    return {
        "name": name,
        "url": url,
        "total_reviews": len(reviews),
        "analysis_date": datetime.now().isoformat(),
        "sentiment_summary": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative
        },
        "bot_stats": {
            "real": real,
            "suspicious": suspicious,
            "bot": bot
        },
        "reviews": reviews
    }


# Datos mock completos para el endpoint /mock-analysis
MOCK_ANALYSIS = {
    "analysis_date": "2026-02-02",
    "businesses": [
        {
            "name": "Clínica San Gabriel",
            "url": "https://maps.google.com/clinica-san-gabriel",
            "total_reviews": 35,
            "category": {"category_id": "salud", "category_name": "Salud", "icon": "🏥"},
            "sentiment_summary": {"positive": 22, "neutral": 8, "negative": 5},
            "bot_stats": {"real": 26, "suspicious": 6, "bot": 3},
            "reviews": [
                {
                    "author": "María García",
                    "text": "Excelente atención médica. El Dr. Rodríguez me atendió con mucha paciencia y profesionalismo.",
                    "rating": 5,
                    "sentiment": "positive",
                    "confidence": 0.95,
                    "bot_score": 10,
                    "bot_classification": "real",
                    "bot_indicators": []
                },
                {
                    "author": "Carlos Mendoza",
                    "text": "Tuve una mala experiencia. Esperé más de 2 horas para mi cita.",
                    "rating": 2,
                    "sentiment": "negative",
                    "confidence": 0.88,
                    "bot_score": 5,
                    "bot_classification": "real",
                    "bot_indicators": []
                },
                {
                    "author": "Usuario123",
                    "text": "Excelente",
                    "rating": 5,
                    "sentiment": "positive",
                    "confidence": 0.70,
                    "bot_score": 75,
                    "bot_classification": "bot",
                    "bot_indicators": ["single_review", "short_text", "generic_phrases"]
                }
            ]
        },
        {
            "name": "Restaurante El Buen Sabor",
            "url": "https://maps.google.com/restaurante-buen-sabor",
            "total_reviews": 48,
            "category": {"category_id": "gastronomia", "category_name": "Gastronomía", "icon": "🍽️"},
            "sentiment_summary": {"positive": 30, "neutral": 12, "negative": 6},
            "bot_stats": {"real": 38, "suspicious": 7, "bot": 3},
            "reviews": [
                {
                    "author": "Sofía Vargas",
                    "text": "La comida es deliciosa. El ceviche es el mejor que he probado en Lima.",
                    "rating": 5,
                    "sentiment": "positive",
                    "confidence": 0.92,
                    "bot_score": 12,
                    "bot_classification": "real",
                    "bot_indicators": []
                }
            ]
        },
        {
            "name": "Hotel Costa del Sol",
            "url": "https://maps.google.com/hotel-costa-sol",
            "total_reviews": 42,
            "category": {"category_id": "hospedaje", "category_name": "Hospedaje", "icon": "🏨"},
            "sentiment_summary": {"positive": 25, "neutral": 10, "negative": 7},
            "bot_stats": {"real": 32, "suspicious": 6, "bot": 4},
            "reviews": [
                {
                    "author": "Miguel Torres",
                    "text": "Habitaciones cómodas y buena ubicación. El desayuno buffet es variado.",
                    "rating": 4,
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "bot_score": 8,
                    "bot_classification": "real",
                    "bot_indicators": []
                }
            ]
        }
    ],
    "comparison": {
        "best_sentiment": "Restaurante El Buen Sabor",
        "most_reviews": "Restaurante El Buen Sabor"
    }
}


def get_mock_data():
    """Retorna los datos simulados de análisis."""
    return MOCK_ANALYSIS
