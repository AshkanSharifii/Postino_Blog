# src/app/api/api_v1/endpoints/posts.py
from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
import logging

from src.app.database.database import get_db
from src.app.crud import post_crud as crud_post
from src.app.models.user_model import User
from src.app.schemas.post_schema import PostCreate, PostOut
from src.app.utils.file import save_image
from src.app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[PostOut])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_post.get_posts(db, skip, limit)


@router.get("/{post_id}", response_model=PostOut)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = crud_post.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostOut)
def create_post(
        title: str = Form(...),
        content: str = Form(...),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    try:
        # Log image information to debug
        logger.info(f"Image received: {type(image)}")
        if image:
            logger.info(f"Image filename: {image.filename}, content_type: {image.content_type}")

        # Safely process the image
        image_path = None
        if image and not image.filename == "":
            image_path = save_image(image)

        # Create the post
        post_in = PostCreate(title=title, content=content)
        return crud_post.create_post(db, post_in, image_path)
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")


@router.put("/{post_id}", response_model=PostOut)
def update_post(
        post_id: int,
        title: str = Form(...),
        content: str = Form(...),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    post = crud_post.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        # Safely process the image
        image_path = None
        if image and not image.filename == "":
            image_path = save_image(image)

        # Update the post
        post_in = PostCreate(title=title, content=content)
        return crud_post.update_post(db, post, post_in, image_path)
    except Exception as e:
        logger.error(f"Error updating post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")


@router.delete("/{post_id}", status_code=204)
def delete_post(
        post_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    post = crud_post.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    crud_post.delete_post(db, post)