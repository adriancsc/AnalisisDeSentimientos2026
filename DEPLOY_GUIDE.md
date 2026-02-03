# 🚀 Guía Completa de Deploy: Firebase + Render

Esta guía te llevará paso a paso para subir tu proyecto a internet.

---

## 📋 Resumen de Pasos

| Paso | Descripción | Tiempo |
|------|-------------|--------|
| 1 | Crear proyecto en Firebase | 5 min |
| 2 | Configurar Firestore | 3 min |
| 3 | Obtener credenciales | 2 min |
| 4 | Probar localmente | 2 min |
| 5 | Subir a GitHub | 5 min |
| 6 | Deploy en Render | 10 min |

**Tiempo total: ~30 minutos**

---

# PASO 1: Crear Proyecto en Firebase

## 1.1 Ir a Firebase Console

1. Abre tu navegador
2. Ve a: **https://console.firebase.google.com**
3. Inicia sesión con tu cuenta de Google

## 1.2 Crear nuevo proyecto

1. Click en el botón azul **"Agregar proyecto"** (o "Create a project")

2. **Nombre del proyecto**: 
   - Escribe: `sentiment-analyzer`
   - Verás que se genera un ID único abajo (ej: `sentiment-analyzer-12345`)
   - Click **"Continuar"**

3. **Google Analytics**:
   - ❌ Desactiva el switch "Habilitar Google Analytics"
   - No lo necesitamos para este proyecto
   - Click **"Crear proyecto"**

4. Espera 30 segundos mientras se crea...

5. Click **"Continuar"** cuando termine

✅ **Ya tienes tu proyecto de Firebase!**

---

# PASO 2: Crear Base de Datos Firestore

## 2.1 Navegar a Firestore

1. En el menú lateral izquierdo, busca **"Build"** (o "Compilación")
2. Click en **"Firestore Database"**

## 2.2 Crear la base de datos

1. Click en el botón **"Create database"** (o "Crear base de datos")

2. **Modo de seguridad**:
   - Selecciona: **"Start in production mode"** (Modo de producción)
   - Click **"Next"** (Siguiente)

3. **Ubicación**:
   - Selecciona: **`us-central`** (o la más cercana a ti)
   - ⚠️ **IMPORTANTE**: Esta ubicación NO se puede cambiar después
   - Click **"Enable"** (Habilitar)

4. Espera ~1 minuto mientras se crea...

✅ **Ya tienes Firestore creado!** (verás una pantalla vacía con "Start collection")

## 2.3 Configurar Reglas de Seguridad

1. En Firestore, click en la pestaña **"Rules"** (Reglas)

2. Reemplaza TODO el contenido con:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. Click **"Publish"** (Publicar)

⚠️ Nota: Estas reglas son para desarrollo. Para producción real deberías agregar autenticación.

---

# PASO 3: Obtener Credenciales

## 3.1 Ir a configuración del proyecto

1. Click en el ícono de ⚙️ **engranaje** (arriba a la izquierda, junto a "Project Overview")
2. Click en **"Project settings"** (Configuración del proyecto)

## 3.2 Crear cuenta de servicio

1. Click en la pestaña **"Service accounts"** (Cuentas de servicio)

2. Verás una sección que dice "Firebase Admin SDK"

3. Asegúrate de que esté seleccionado **"Python"**

4. Click en el botón **"Generate new private key"** (Generar nueva clave privada)

5. Aparecerá un popup de confirmación → Click **"Generate key"**

6. **Se descargará un archivo JSON** automáticamente
   - El nombre será algo como: `sentiment-analyzer-12345-firebase-adminsdk-xxxxx.json`

## 3.3 Guardar las credenciales

1. **Renombra** el archivo descargado a: `firebase-credentials.json`

2. **Mueve** el archivo a la carpeta:
   ```
   c:\NLP - Parcial Taller Social\backend\firebase-credentials.json
   ```

3. **Verifica** que el archivo esté en la ubicación correcta:
   ```
   backend/
   ├── main.py
   ├── firebase-credentials.json   ← AQUÍ
   └── ...
   ```

---

# PASO 4: Probar Localmente

## 4.1 Reiniciar el backend

1. Ve a la terminal donde está corriendo uvicorn
2. Presiona `Ctrl + C` para detenerlo
3. Vuelve a ejecutar:
   ```
   uvicorn main:app --reload --port 8000
   ```

4. Deberías ver en la terminal:
   ```
   ✅ Firestore conectado exitosamente
   📦 Usando Firestore para historial
   ```

## 4.2 Probar el dashboard

1. Abre `frontend/index.html` en el navegador
2. Pega una URL de Google Maps
3. Click "Analizar"
4. **Verifica en Firebase Console**:
   - Ve a Firestore Database
   - Deberías ver una colección "businesses" con tu análisis

✅ **Si ves los datos en Firebase, todo funciona!**

---

# PASO 5: Subir a GitHub

## 5.1 Crear repositorio en GitHub

1. Ve a: **https://github.com/new**

2. **Repository name**: `sentiment-analyzer`

3. Deja todo lo demás por defecto

4. Click **"Create repository"**

5. NO cierres esta página, la necesitarás

## 5.2 Inicializar Git (en tu proyecto)

Abre una terminal en `c:\NLP - Parcial Taller Social\` y ejecuta:

```bash
# Inicializar repositorio
git init

# Agregar todos los archivos
git add .

# Verificar que firebase-credentials.json NO está incluido
git status
```

⚠️ **IMPORTANTE**: Verifica que `firebase-credentials.json` aparezca como "Untracked" o no aparezca. Si aparece en verde, ejecuta:
```bash
git reset backend/firebase-credentials.json
```

## 5.3 Hacer commit y push

```bash
# Crear commit
git commit -m "Initial commit - Sentiment Analyzer"

# Conectar con GitHub (reemplaza TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/sentiment-analyzer.git

# Subir código
git branch -M main
git push -u origin main
```

Te pedirá credenciales de GitHub (o usar token).

---

# PASO 6: Deploy en Render

## 6.1 Crear cuenta en Render

1. Ve a: **https://render.com**
2. Click **"Get Started for Free"**
3. Click **"GitHub"** para registrarte con tu cuenta de GitHub
4. Autoriza el acceso

## 6.2 Desplegar el Backend

1. En el Dashboard de Render, click **"New +"**
2. Selecciona **"Web Service"**

3. **Conectar repositorio**:
   - Busca `sentiment-analyzer`
   - Click **"Connect"**

4. **Configuración del servicio**:
   | Campo | Valor |
   |-------|-------|
   | Name | `sentiment-api` |
   | Region | `Oregon (US West)` |
   | Branch | `main` |
   | Root Directory | `backend` |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. **Plan**: Selecciona **"Free"**

6. **Variables de entorno** (MUY IMPORTANTE):
   - Click **"Advanced"**
   - Click **"Add Environment Variable"**
   - Key: `FIREBASE_CREDENTIALS_JSON`
   - Value: **Abre tu archivo `firebase-credentials.json` y copia TODO el contenido**
     - Ctrl+A para seleccionar todo
     - Ctrl+C para copiar
     - Pégalo en el campo Value

7. Click **"Create Web Service"**

8. Espera 3-5 minutos mientras se despliega...

9. Cuando termine, verás una URL como:
   ```
   https://sentiment-api.onrender.com
   ```
   **Copia esta URL!**

## 6.3 Desplegar el Frontend

1. Click **"New +"** → **"Static Site"**

2. Conecta el mismo repositorio `sentiment-analyzer`

3. **Configuración**:
   | Campo | Valor |
   |-------|-------|
   | Name | `sentiment-dashboard` |
   | Branch | `main` |
   | Root Directory | `frontend` |
   | Publish Directory | `.` |

4. Click **"Create Static Site"**

5. Espera 1-2 minutos...

## 6.4 Conectar Frontend con Backend

1. En tu proyecto local, edita `frontend/app.js`

2. Cambia la línea 7:
   ```javascript
   // ANTES:
   const API_BASE_URL = 'http://localhost:8000';
   
   // DESPUÉS (usa TU URL de Render):
   const API_BASE_URL = 'https://sentiment-api.onrender.com';
   ```

3. Guarda, commit y push:
   ```bash
   git add frontend/app.js
   git commit -m "Update API URL for production"
   git push
   ```

4. Render actualizará automáticamente en ~1 minuto

---

# ✅ Verificación Final

1. Abre la URL de tu frontend (ej: `https://sentiment-dashboard.onrender.com`)

2. Ingresa una URL de Google Maps

3. Click "Analizar"

4. **Si funciona**: 🎉 ¡Tu app está en internet!

5. **Verifica persistencia**:
   - Cierra el navegador
   - Vuelve a abrir la URL
   - El historial debería seguir ahí

---

# 🔧 Solución de Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| "Firestore no conecta" | Credenciales mal copiadas | Copia el JSON completo, incluyendo las llaves {} |
| "CORS error" | URL del backend mal | Verifica que sea https:// y sin / al final |
| Backend se duerme | Plan gratuito | Normal, tarda ~30s en despertar |
| "Error 500" | Error en código | Revisa logs en Render Dashboard |

---

# 📝 Notas Importantes

1. **El plan gratuito de Render** pone tu app a "dormir" después de 15 min sin uso. La primera visita tarda ~30 segundos en cargar.

2. **Las credenciales** nunca deben subirse a GitHub. Por eso usamos la variable de entorno.

3. **Para compartir tu app**, usa la URL del frontend, no la del backend.

---

¡Listo! Tu app de análisis de sentimientos está en internet 🎉
