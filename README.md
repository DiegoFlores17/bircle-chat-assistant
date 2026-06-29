# TechShop Assistant

A customer service chatbot for a fictional electronics store, built with FastAPI and powered by Groq (Llama 3.3 70B).

## Features

- Conversational assistant specialized in electronics (smartphones, laptops, headphones, tablets)
- Per-user conversation history maintained in memory
- Off-topic message filtering — no LLM tokens wasted on unrelated queries
- Graceful error handling — clients always receive a friendly response
- Simple chat UI included

## Requirements

- Python 3.9+
- A free [Groq API key](https://console.groq.com)

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/DiegoFlores17/bircle-chat.git
cd bircle-chat

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your Groq API key
```

`.env` file:
```
GROQ_API_KEY=your_key_here
```

## Running the server

```bash
uvicorn main:app --reload
```

The server starts at `http://localhost:8000`.

> **No API key?** The service runs in mock mode with predefined responses — no setup required.

## Testing

**Chat UI** — open in your browser:
```
http://localhost:8000/ui
```

**Swagger UI** (interactive API docs):
```
http://localhost:8000/docs
```

**curl:**
```bash
# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "message": "qué notebooks tienen?"}'

# Health check
curl http://localhost:8000/health

# Clear conversation history
curl -X DELETE http://localhost:8000/chat/u1
```

## API Reference

### `POST /chat`
```json
// Request
{ "user_id": "string", "message": "string" }

// Response
{ "response": "string", "user_id": "string" }
```

### `GET /health`
```json
{ "status": "ok" }
```

### `DELETE /chat/{user_id}`
Clears the conversation history for the given user.

## Project Structure

```
├── main.py          # FastAPI app and endpoints
├── llm.py           # Groq integration, mock, and off-topic filter
├── models.py        # Pydantic request/response models
├── requirements.txt
├── static/
│   └── index.html   # Chat UI
└── .env.example
```
