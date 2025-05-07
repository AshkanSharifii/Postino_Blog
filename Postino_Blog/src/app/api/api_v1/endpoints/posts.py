# posts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
import logging

from src.app.database.database import get_db
from src.app.schemas.post_schema import PostCreate, PostOut
from src.app.crud import post_crud
from src.app.utils.file import save_image
from src.app.models.user_model import User
from src.app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------- helpers ----------
def _make_out(p) -> PostOut:
    return PostOut(
        id=p.id,
        title=p.title,
        content=p.content,
        image_url=p.image_url,
        tags=[t.name for t in p.tags],
        created_at=p.created_at,
        updated_at=p.updated_at,
    )

# ---------- routes ----------
@router.get("/", response_model=List[PostOut])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
):
    posts = post_crud.get_posts(db, skip=skip, limit=limit, tag_name=tag)
    return [_make_out(p) for p in posts]

@router.get("/{post_id}", response_model=PostOut)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _make_out(post)

@router.post("/", response_model=PostOut)
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    tags: Optional[str] = Form(None),          # ← appears in Swagger
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    img_path = save_image(image) if image and image.filename else None
    obj_in   = PostCreate(title=title, content=content, tags=tags)
    post     = post_crud.create_post(db, obj_in=obj_in, image_url=img_path)
    return _make_out(post)

@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    tags: Optional[str] = Form(None),          # send "" to clear all
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    img_path = save_image(image) if image and image.filename else None
    obj_in   = PostCreate(title=title, content=content, tags=tags)
    post     = post_crud.update_post(db, post=post, obj_in=obj_in, image_url=img_path)
    return _make_out(post)

@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post_crud.delete_post(db, post)
