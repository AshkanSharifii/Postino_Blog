from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    image_url: Optional[str]  # Changed from HttpUrl to str
    created_at: datetime
    updated_at: Optional[datetime]  # Made this more explicit

    class Config:
        orm_mode = True
        from_attributes = True  # Updated from orm_mode (which is deprecated)