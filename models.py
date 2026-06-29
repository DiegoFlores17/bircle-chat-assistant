from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    user_id: str


class HealthResponse(BaseModel):
    status: str


class DeleteResponse(BaseModel):
    message: str
