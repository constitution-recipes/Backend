from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = "새 채팅"

class ChatSessionOut(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    last_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class ChatMessageCreate(BaseModel):
    session_id: str
    role: str
    content: str

class ChatMessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime 