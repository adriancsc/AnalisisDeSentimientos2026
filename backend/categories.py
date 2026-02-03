"""
Clasificador de rubros de negocios.
Detecta automáticamente el tipo de negocio basándose en palabras clave.
"""

# Definición de rubros y palabras clave
CATEGORIES = {
    "salud": {
        "icon": "🏥",
        "name": "Salud",
        "keywords": [
            "clínica", "clinica", "hospital", "consultorio", "médico", "medico",
            "dental", "dentista", "oftalmólogo", "oftalmologo", "pediatra",
            "ginecólogo", "ginecologo", "laboratorio", "farmacia", "botica",
            "centro médico", "centro medico", "policlínico", "policlinico",
            "san gabriel", "ricardo palma", "good hope", "javier prado"
        ]
    },
    "gastronomia": {
        "icon": "🍽️",
        "name": "Gastronomía",
        "keywords": [
            "restaurante", "restaurant", "café", "cafe", "cafetería", "cafeteria",
            "bar", "pizzería", "pizzeria", "cevichería", "cevicheria",
            "chifa", "pollería", "polleria", "panadería", "panaderia",
            "heladería", "heladeria", "pastelería", "pasteleria", "comida",
            "sushi", "burger", "hamburguesería", "hamburgueseria", "cocina"
        ]
    },
    "hospedaje": {
        "icon": "🏨",
        "name": "Hospedaje",
        "keywords": [
            "hotel", "hostal", "hospedaje", "alojamiento", "resort",
            "airbnb", "bed and breakfast", "motel", "lodge", "inn"
        ]
    },
    "retail": {
        "icon": "🛒",
        "name": "Retail",
        "keywords": [
            "tienda", "supermercado", "minimarket", "bodega", "market",
            "plaza vea", "wong", "metro", "tottus", "vivanda",
            "saga", "ripley", "oechsle", "paris", "electrodomésticos"
        ]
    },
    "educacion": {
        "icon": "🎓",
        "name": "Educación",
        "keywords": [
            "universidad", "colegio", "instituto", "academia", "escuela",
            "centro de estudios", "capacitación", "capacitacion", "idiomas",
            "pucp", "ulima", "upc", "usil", "san marcos"
        ]
    },
    "servicios": {
        "icon": "💼",
        "name": "Servicios",
        "keywords": [
            "banco", "notaría", "notaria", "abogado", "contador",
            "aseguradora", "seguro", "inmobiliaria", "agencia", "consultoría",
            "bcp", "interbank", "bbva", "scotiabank"
        ]
    },
    "otros": {
        "icon": "📍",
        "name": "Otros",
        "keywords": []
    }
}


def classify_business(business_name: str, url: str = "") -> dict:
    """
    Clasifica un negocio en su rubro correspondiente.
    
    Args:
        business_name: Nombre del negocio
        url: URL de Google Maps (opcional)
    
    Returns:
        dict con category_id, category_name, icon
    """
    # Combinar nombre y URL para buscar keywords
    text_to_analyze = f"{business_name} {url}".lower()
    
    # Buscar coincidencias
    for category_id, category_data in CATEGORIES.items():
        if category_id == "otros":
            continue
            
        for keyword in category_data["keywords"]:
            if keyword.lower() in text_to_analyze:
                return {
                    "category_id": category_id,
                    "category_name": category_data["name"],
                    "icon": category_data["icon"]
                }
    
    # Si no hay coincidencia, retornar "otros"
    return {
        "category_id": "otros",
        "category_name": "Otros",
        "icon": "📍"
    }


def get_all_categories() -> list:
    """Retorna lista de todas las categorías disponibles."""
    return [
        {
            "id": cat_id,
            "name": cat_data["name"],
            "icon": cat_data["icon"]
        }
        for cat_id, cat_data in CATEGORIES.items()
    ]
