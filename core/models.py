from pydantic import BaseModel, validator
from typing import Any, Optional
import uuid

class PublishMessageModel(BaseModel):
    id: str
    payload: Any

    @validator("id")
    def valid_uuid(cls, v):
        try:
            uuid.UUID(v)
        except Exception:
            raise ValueError("message.id must be a valid UUID string")
        return v

class WSMessage(BaseModel):
    type: str
    topic: Optional[str] = None
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    message: Optional[PublishMessageModel] = None
    last_n: Optional[int] = None
