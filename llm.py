import os

from groq import AsyncGroq, AuthenticationError

SYSTEM_PROMPT = """Eres Alex, un asistente de atención al cliente amable y conciso de TechShop, una tienda de electrónica.

Ayudas a los clientes con:
- Recomendaciones de productos (smartphones, laptops, auriculares, tablets, accesorios)
- Precios aproximados en USD
- Información sobre garantías (12 meses oficial en todos los productos, planes extendidos disponibles)
- Soporte técnico básico y resolución de problemas

Reglas:
- Responde SIEMPRE en español, sin importar el idioma en que te escriban
- Sé cálido, profesional y conciso — máximo 3 oraciones por respuesta
- Si no tenés datos exactos de un producto, dá rangos de precio realistas
- Nunca inventes números de modelo ni disponibilidad de stock
- Si el problema técnico es complejo, sugerí acercarse a una sucursal de TechShop
- Siempre ofrecé una pregunta de seguimiento para mantener la conversación útil
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


def _is_on_topic(message: str) -> bool:
    lower = message.lower()
    return any(kw in lower for kw in _ON_TOPIC_KEYWORDS)


async def get_llm_response(message: str, history: list[dict]) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return _get_mock_response(message)

    if not _is_on_topic(message):
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
