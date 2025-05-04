"""
Thin wrapper around the official MinIO SDK that
* creates buckets on first run
* enables versioning
* exposes the underlying Minio() instance as `.client`
"""
from __future__ import annotations
from typing import Iterable
from minio import Minio
from minio.versioningconfig import VersioningConfig, ENABLED

class MinioClient:
    def __init__(
        self,
        *,
        url: str,
        access_key: str,
        secret_key: str,
        buckets: Iterable[str],
        secure: bool = False,
    ) -> None:
        self.client = Minio(
            endpoint=url,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._make_buckets(buckets)

    # ------------------------------------------------------------------ #
    def _make_buckets(self, buckets: Iterable[str]) -> None:
        """Create each bucket once and switch versioning on."""
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                self.client.set_bucket_versioning(
                    bucket, VersioningConfig(ENABLED)
                )
