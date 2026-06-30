# TechShop Assistant

Asistente de atención al cliente para una tienda ficticia de electrónica, construido con FastAPI y Groq (Llama 3.3 70B).

## Características

- Conversación especializada en electrónica (smartphones, notebooks, auriculares, tablets)
- Historial de conversación por usuario
- Filtro de mensajes fuera de tema — no consume tokens innecesarios
- Manejo de errores: el cliente siempre recibe una respuesta amigable
- Interfaz de chat incluida

## Requisitos

- Python 3.9+
- Una [API key gratuita de Groq](https://console.groq.com)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/DiegoFlores17/bircle-chat-assistant.git
cd bircle-chat-assistant
```

### 2. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Windows: `.venv\Scripts\activate`

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la API key

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
GROQ_API_KEY=tu_key_aqui
```

La key se obtiene gratis en [console.groq.com](https://console.groq.com) → API Keys → Create API Key.

> **Sin API key:** el servicio funciona igual en modo mock con respuestas predefinidas.

### 5. Iniciar el servidor

```bash
uvicorn main:app --reload
```


---

## Cómo probarlo

### Opción A — Interfaz visual

Abrí en el browser:

```
http://localhost:8000/ui
```

### Opción B — Swagger UI (documentación interactiva)

```
http://localhost:8000/docs
```

### Opción C — curl

```bash
# Enviar un mensaje
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "message": "qué notebooks tienen?"}'

# Verificar que el servidor está activo
curl http://localhost:8000/health

# Limpiar el historial de un usuario
curl -X DELETE http://localhost:8000/chat/u1
```

---

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/chat` | Enviar un mensaje al asistente |
| `GET` | `/health` | Verificar estado del servidor |
| `DELETE` | `/chat/{user_id}` | Limpiar historial de un usuario |

### POST /chat

Request:
```json
{ "user_id": "string", "message": "string" }
```

Response:
```json
{ "response": "string", "user_id": "string" }
```

---

## Estructura del proyecto

```
├── main.py          # App FastAPI y endpoints
├── llm.py           # Integración con Groq, mock y filtro de temas
├── models.py        # Modelos Pydantic
├── requirements.txt
└── static/
    └── index.html   # Interfaz de chat
```
