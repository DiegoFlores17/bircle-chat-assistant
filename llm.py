import json
import os

from groq import AsyncGroq, AuthenticationError

SYSTEM_PROMPT = """Eres Alex, un asistente de atención al cliente amable y conciso de TechShop, una tienda de electrónica.

Catálogo disponible:
- Smartphones: iPhone 15, iPhone 15 Plus, iPhone 15 Pro, iPhone 15 Pro Max, iPhone 16, iPhone 16 Plus, iPhone 16 Pro, iPhone 16 Pro Max — Samsung Galaxy S24, S24+, S24 Ultra, S25, S25+, S25 Ultra, A55, A35 — Motorola Edge 50, Moto G85
- Notebooks: MacBook Air M3, MacBook Pro M3, MacBook Pro M4 — Lenovo ThinkPad X1 Carbon, IdeaPad 5 — HP Spectre x360, Omen 17 — Dell XPS 15, Inspiron 16
- Auriculares: AirPods 4, AirPods Pro 2 — Sony WH-1000XM5 — Bose QuietComfort Ultra — Samsung Galaxy Buds3 Pro — JBL Tour Pro 3
- Tablets: iPad 10ma gen, iPad Air M2, iPad Pro M4 — Samsung Galaxy Tab S9, Tab S9 FE
- Accesorios: cargadores MagSafe, cables USB-C, fundas, protectores de pantalla, hubs USB-C

Precios aproximados en USD:
- iPhones: desde $700 (iPhone 15) hasta $1,300 (iPhone 16 Pro Max)
- Samsung gama alta: $800–$1,300 / gama media: $350–$550
- MacBooks: desde $1,100 hasta $2,500
- Notebooks Windows: desde $600 hasta $1,800
- Auriculares: desde $50 hasta $400
- Tablets: desde $350 hasta $1,100

Garantías: 12 meses oficial en todos los productos. Planes extendidos de hasta 3 años disponibles.

Reglas generales:
- Responde SIEMPRE en español, sin importar el idioma en que te escriban
- Sé cálido, profesional y conciso — máximo 3 oraciones por respuesta
- Todos los productos del catálogo están en stock
- Nunca inventes modelos fuera del catálogo ni fechas de reposición
- Si el problema técnico es complejo, sugerí acercarse a una sucursal de TechShop

Flujo de compra (seguí este orden estrictamente, UNA pregunta por turno):
- Cuando el usuario muestre intención de comprar, recolectá TODOS estos datos antes de finalizar:
  1. Categoría de producto (si no lo mencionó): ej. smartphone, notebook, auriculares
  2. Modelo específico (ofrecé las opciones del catálogo para esa categoría)
  3. Almacenamiento o capacidad (si aplica al producto: 128GB, 256GB, 512GB, etc.)
  4. Color o variante (si aplica: negro, blanco, azul, etc.)
  5. Confirmación del precio: mencioná el precio aproximado del modelo elegido
- Solo cuando tengas los 5 datos recolectados, resumí la elección completa y decí: "¡Perfecto! Para conectarte con un asesor y cerrar la compra, escribí 'confirmar compra'."
- No hagas más de una pregunta por turno.
- No sugieras "confirmar compra" hasta tener producto, modelo, almacenamiento, color y precio confirmados.
- No ofrezcas contacto directo — eso lo maneja el sistema automáticamente.
"""

_MOCK_RESPONSES: list[tuple[list[str], str]] = [
    (
        ["precio", "cuesta", "vale", "cost", "price"],
        "En TechShop manejamos precios muy competitivos. Los smartphones van desde $200 hasta $1,200, notebooks desde $500 hasta $2,000, y auriculares desde $30 hasta $400. ¿Qué producto te interesa?",
    ),
    (
        ["celular", "smartphone", "iphone", "samsung", "telefono"],
        "Contamos con smartphones de Samsung, Apple y Motorola. Los rangos van desde $200 para gama media hasta $1,200 para los flagships. ¿Cuál es tu presupuesto aproximado?",
    ),
    (
        ["notebook", "laptop", "computadora", "pc"],
        "Nuestras notebooks van desde modelos de estudio a $500 hasta workstations profesionales a $2,000+. ¿Para qué uso la necesitás — estudio, trabajo, gaming?",
    ),
    (
        ["auricular", "headphone", "headset", "audio"],
        "Tenemos auriculares desde $30 hasta $400. Si buscás cancelación de ruido activa, nuestros modelos premium desde $150 son excelentes. ¿Los necesitás con cable o inalámbricos?",
    ),
    (
        ["garantia", "garantía", "warranty"],
        "Todos los productos de TechShop incluyen garantía oficial de 12 meses. También ofrecemos planes de garantía extendida de hasta 3 años. ¿Necesitás más detalles sobre algún producto?",
    ),
    (
        ["soporte", "support", "reparacion", "reparación", "arreglar", "problema"],
        "Para soporte técnico podés acercarte a cualquiera de nuestras sucursales — hacemos diagnóstico gratuito. También podés describir el problema aquí y te ayudo con los pasos básicos.",
    ),
    (
        ["tablet", "ipad"],
        "Contamos con tablets Android desde $150 y iPads desde $350. Son ideales para lectura, trabajo remoto y entretenimiento. ¿Qué uso principal le vas a dar?",
    ),
]

_MOCK_DEFAULT = (
    "Gracias por contactarte con TechShop. Estoy aquí para ayudarte con productos, precios, "
    "garantías y soporte técnico. ¿En qué puedo ayudarte hoy?"
)


def _get_mock_response(message: str) -> str:
    lower = message.lower()
    for keywords, response in _MOCK_RESPONSES:
        if any(kw in lower for kw in keywords):
            return response
    return _MOCK_DEFAULT


_ON_TOPIC_KEYWORDS = {
    "celular", "smartphone", "telefono", "iphone", "samsung", "motorola", "android",
    "notebook", "laptop", "computadora", "pc", "mac", "macbook",
    "auricular", "headphone", "headset", "audio", "parlante", "speaker",
    "tablet", "ipad",
    "precio", "costo", "vale", "cuesta", "presupuesto", "oferta",
    "garantia", "garantía", "warranty", "soporte", "reparacion", "reparación",
    "arreglar", "problema", "falla", "no funciona", "roto",
    "bateria", "batería", "carga", "cargador", "cable", "pantalla", "camara", "cámara",
    "comprar", "producto", "stock", "disponible", "accesorio",
    "tv", "televisor", "monitor", "consola", "gaming", "juego",
    "wifi", "bluetooth", "internet", "teclado", "mouse", "impresora",
    "memoria", "disco", "almacenamiento", "ram",
    "techshop", "tienda", "regalo",
}

_OFF_TOPIC_RESPONSE = (
    "Solo puedo ayudarte con consultas sobre productos de electrónica, precios, "
    "garantías y soporte técnico de TechShop. ¿En qué puedo ayudarte?"
)


_ALWAYS_ALLOW = {
    "hola", "buenas", "buen dia", "buen día", "buenos dias", "buenos días",
    "buenas tardes", "buenas noches", "hey", "hi", "hello", "saludos",
    "gracias", "de nada", "ok", "okay", "sí", "si", "no", "chau", "adios",
    "adiós", "hasta luego", "ayuda", "ayudame", "necesito ayuda",
    "confirmar compra", "confirmo la compra", "confirmo compra", "quiero confirmar",
}


def _is_on_topic(message: str) -> bool:
    lower = message.lower().strip()
    if any(kw in lower for kw in _ALWAYS_ALLOW):
        return True
    return any(kw in lower for kw in _ON_TOPIC_KEYWORDS)


async def get_llm_response(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return _get_mock_response(message)

    if not history and not _is_on_topic(message):
        return _OFF_TOPIC_RESPONSE

    client = AsyncGroq(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history,
                {"role": "user", "content": message},
            ],
        )
    except AuthenticationError:
        raise RuntimeError("API key inválida. Verificá el valor de GROQ_API_KEY en tu archivo .env.")
    return response.choices[0].message.content


async def extract_purchase_details(history: list[dict]) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {}

    client = AsyncGroq(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=200,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Analizá la conversación y extraé los detalles del producto que el usuario quiere comprar. "
                        "Respondé SOLO con un JSON válido con exactamente estos campos: "
                        '{"producto": "", "modelo": "", "almacenamiento": "", "color": "", "precio aproximado": ""}. '
                        "Si algún campo no fue mencionado, dejá el valor como cadena vacía."
                    ),
                },
                *history,
            ],
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}
