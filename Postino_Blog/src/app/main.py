from fastapi import FastAPI

from src.app.database.database import engine, Base, SessionLocal
from src.app.core.config import settings
from src.app.crud.user_crud import get_user_by_username, create_user
from src.app.schemas.user_schema import UserCreate
from src.app.api.api_v1.routers import api_router

# --- NEW: eager‑import so the client creates the bucket once -------------
from src.app.services.minio_client import MinioClient
MinioClient(                                     # noqa: E402
    url=settings.minio_endpoint,
    access_key=settings.minio_root_user,  # ← updated
    secret_key=settings.minio_root_password,
    buckets=[settings.minio_bucket],
    secure=False,
)
# -------------------------------------------------------------------------

app = FastAPI()

# 1. tables
Base.metadata.create_all(bind=engine)

# 2. default user
def init_default_user() -> None:
    db = SessionLocal()
    try:
        email = settings.default_user_email
        if not get_user_by_username(db, email):
            user_in = UserCreate(
                username=email,
                email=email,
                password=settings.default_user_password,
            )
            create_user(db, user_in)
            print(f"✨ Created default user {email}")
    finally:
        db.close()

@app.on_event("startup")
def on_startup() -> None:
    init_default_user()

# 3. mount api
app.include_router(api_router, prefix="/api/v1")
