# src/app/schemas/post_schema.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class PostBase(BaseModel):
    title: str
    content: str
    # UI sends comma‑separated names, e.g. "هواوی,انویدیا"
    tags: Optional[str] = Field(
        default=None,
        description="Comma‑separated tag names sent by the form"
    )

class PostCreate(PostBase):
    pass

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    # ↓ give the field a default + example so Swagger shows it
    tags: List[str] = Field(
        default=[],
        example=["هواوی", "انویدیا"],
        description="List of tag names attached to the post"
    )
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
