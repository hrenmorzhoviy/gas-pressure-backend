from miniopy_async.api import Minio

from core.config import settings


client = Minio(
    settings.MINIO_HOST,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)


async def get_minio() -> Minio:
    if not await client.bucket_exists(settings.MINIO_BUCKET):
        await client.make_bucket(settings.MINIO_BUCKET)
    return client
