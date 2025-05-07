# tags.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.database.database import get_db
from src.app.models.tag_model import Tag

router = APIRouter()

@router.get("/", response_model=List[str])
def list_all_tags(db: Session = Depends(get_db)):
    return [t.name for t in db.query(Tag).order_by(Tag.name).all()]
