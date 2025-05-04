# src/app/crud/post_crud.py

from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.post_model import Post
from src.app.schemas.post_schema import PostCreate


def get_posts(db: Session, skip: int = 0, limit: int = 100) -> list[Post]:
    return db.query(Post).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(
    db: Session,
    post_in: PostCreate,
    image_url: Optional[str] = None,
) -> Post:
    """
    Create a new Post, storing the image_url (from MinIO) if provided.
    """
    post = Post(
        title=post_in.title,
        content=post_in.content,
        image_url=image_url,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(
    db: Session,
    post: Post,
    data: PostCreate,
    image_url: Optional[str] = None,
) -> Post:
    """
    Update an existing Post. If a new image_url is provided,
    overwrite the old one.
    """
    post.title = data.title
    post.content = data.content
    if image_url is not None:
        post.image_url = image_url
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()
