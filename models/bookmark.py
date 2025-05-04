from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Bookmark(BaseModel):
    id: Optional[str] = Field(None, description="북마크 고유 ID")
    user_id: str = Field(..., description="유저 ID")
    recipe_id: str = Field(..., description="레시피 ID")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="생성일시")

    class Config:
        orm_mode = True 