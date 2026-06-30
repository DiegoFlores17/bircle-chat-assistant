from pydantic import BaseModel, field_validator

MESSAGE_MAX_LENGTH = 1000


class ChatRequest(BaseModel):
    user_id: str
    message: str

    @field_validator("user_id")
    @classmethod
    def user_id_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_id no puede estar vacío o contener solo espacios.")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_valid(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message no puede estar vacío.")
        if len(v) > MESSAGE_MAX_LENGTH:
            raise ValueError(f"message excede el límite de {MESSAGE_MAX_LENGTH} caracteres.")
        return v


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
