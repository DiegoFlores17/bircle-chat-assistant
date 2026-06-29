from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    user_id: str
    end_conversation: bool = False
    purchase_ready: bool = False
    purchase_details: dict = {}


class HealthResponse(BaseModel):
    status: str


class DeleteResponse(BaseModel):
    message: str
