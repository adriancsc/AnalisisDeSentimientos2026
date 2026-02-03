# 📊 Análisis de Sentimientos en Redes Sociales

Sistema de análisis de sentimientos para reseñas de Google Maps con **detección de bots** y **clasificación por rubro**.

## ✨ Características

- ✅ Análisis de sentimientos (positivo/neutral/negativo)
- ✅ Detección de reseñas falsas (bot score 0-100%)
- ✅ Clasificación automática de rubros
- ✅ Historial persistente (Firestore)
- ✅ Comparativa entre negocios
- ✅ Dashboard interactivo

## 🚀 Instalación Local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
Abrir `frontend/index.html` en el navegador.

## ☁️ Deploy en la Nube

Ver [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) para instrucciones completas de:
- Configuración de Firebase/Firestore
- Deploy en Render (gratis)

## 🛠️ Tecnologías

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Base de datos**: Firebase Firestore
- **Hosting**: Render

## 👥 Equipo

NLP - Evaluación Parcial 2026
