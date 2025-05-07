# post_crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from src.app.models.post_model import Post
from src.app.models.tag_model import Tag
from src.app.schemas.post_schema import PostCreate
from src.app.crud.tag_crud import get_or_create_tags

# ---------- read ----------
def get_posts(
    db: Session, skip: int = 0, limit: int = 100, tag_name: Optional[str] = None
) -> List[Post]:
    q = db.query(Post)
    if tag_name:
        q = q.join(Post.tags).filter(Tag.name == tag_name)
    return q.offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

# ---------- write ----------
def create_post(
    db: Session,
    obj_in: PostCreate,
    image_url: Optional[str] = None,
) -> Post:
    tag_names = (
        [t.strip() for t in obj_in.tags.split(",") if t.strip()]
        if obj_in.tags
        else []
    )

    post = Post(
        title=obj_in.title,
        content=obj_in.content,
        image_url=image_url,
    )
    if tag_names:
        post.tags = get_or_create_tags(db, tag_names)

    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def update_post(
    db: Session,
    post: Post,
    obj_in: PostCreate,
    image_url: Optional[str] = None,
) -> Post:
    post.title   = obj_in.title
    post.content = obj_in.content
    if image_url is not None:
        post.image_url = image_url

    if obj_in.tags is not None:              # replace tags only if sent
        tag_names = [t.strip() for t in obj_in.tags.split(",") if t.strip()]
        post.tags = get_or_create_tags(db, tag_names)

    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()
