# src/app/utils/file.py
"""
Save an image (FastAPI/Starlette UploadFile _or_ raw bytes) to MinIO
and return the object URL.
"""

from __future__ import annotations

import os
import uuid
from io import BytesIO
from typing import Optional, Union

from fastapi import UploadFile, HTTPException
from starlette.datastructures import UploadFile as StarletteUploadFile
from minio.error import S3Error

from src.app.core.config import settings
from src.app.services.minio_client import MinioClient

# --------------------------------------------------------------------- #
# Shared MinIO SDK client
# --------------------------------------------------------------------- #
_minio = MinioClient(
    url=settings.minio_endpoint,
    access_key=settings.minio_root_user,
    secret_key=settings.minio_root_password,
    buckets=[settings.minio_bucket],
    secure=False,
).client


def save_image(
    image: Union[UploadFile, StarletteUploadFile, bytes, None]
) -> Optional[str]:
    """
    Accept either:
    • FastAPI / Starlette UploadFile
    • raw `bytes`
    • `None`  → returns None

    Uploads the file to MinIO and returns the public URL.
    """
    if image is None:
        return None

    # ------------------------------------------------------ #
    # Handle any UploadFile‑like object (FastAPI or Starlette)
    # ------------------------------------------------------ #
    if hasattr(image, "file"):
        stream = image.file
        stream.seek(0, os.SEEK_END)
        length = stream.tell()
        stream.seek(0)

        ext = (
            image.filename.rsplit(".", 1)[-1]
            if image.filename and "." in image.filename
            else "bin"
        )
        object_name = f"{uuid.uuid4().hex}.{ext}"
        content_type = getattr(image, "content_type", None) or "application/octet-stream"

    # ----------------- raw bytes --------------------------- #
    else:
        if not isinstance(image, (bytes, bytearray)):
            raise HTTPException(400, "Expected file upload or bytes")
        stream = BytesIO(image)
        length = len(image)
        object_name = f"{uuid.uuid4().hex}.jpg"
        content_type = "image/jpeg"

    # ----------------- upload to MinIO --------------------- #
    try:
        _minio.put_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
            data=stream,
            length=length,
            content_type=content_type,
        )
    except S3Error as err:
        raise HTTPException(500, f"Image upload failed: {err}")

    return f"http://{settings.minio_endpoint}/{settings.minio_bucket}/{object_name}"
