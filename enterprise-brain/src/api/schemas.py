from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    pro_mode: bool = False

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None

class UploadResponse(BaseModel):
    filename: str
    status: str
