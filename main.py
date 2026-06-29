import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

load_dotenv()

from llm import extract_purchase_details, get_llm_response
from models import ChatRequest, ChatResponse, DeleteResponse, HealthResponse

app = FastAPI(title="TechShop Assistant", version="1.0.0")
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")

# user_id -> list of {"role": "user"|"assistant", "content": str}
_conversation_store: dict[str, list[dict]] = {}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Missing or invalid fields. Required: user_id (string), message (string)."},
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


_CLOSING_KEYWORDS = {"chau", "adiós", "adios", "hasta luego", "bye", "nos vemos", "gracias", "muchas gracias"}

_PURCHASE_READY_KEYWORDS = {"confirmar compra", "confirmo la compra", "confirmo compra", "quiero confirmar"}

def _is_closing(message: str) -> bool:
    lower = message.lower().strip()
    return len(lower.split()) <= 4 and any(kw in lower for kw in _CLOSING_KEYWORDS)

def _is_purchase_ready(message: str) -> bool:
    lower = message.lower().strip()
    return any(kw in lower for kw in _PURCHASE_READY_KEYWORDS)


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    history = _conversation_store.get(body.user_id, [])

    ending  = _is_closing(body.message)
    buying  = _is_purchase_ready(body.message)

    try:
        reply = await get_llm_response(body.message, history)
    except Exception as exc:
        logger.error("LLM error for user %s: %s", body.user_id, exc)
        reply = "En este momento no puedo procesar tu consulta. ¿Qué producto de TechShop te interesa ver?"

    _conversation_store[body.user_id] = history + [
        {"role": "user", "content": body.message},
        {"role": "assistant", "content": reply},
    ]

    details = await extract_purchase_details(history) if buying else {}

    return ChatResponse(response=reply, user_id=body.user_id, end_conversation=ending, purchase_ready=buying, purchase_details=details)


@app.delete("/chat/{user_id}", response_model=DeleteResponse)
async def clear_history(user_id: str):
    _conversation_store.pop(user_id, None)
    return DeleteResponse(message=f"History cleared for user '{user_id}'.")
