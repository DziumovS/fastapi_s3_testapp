from contextlib import asynccontextmanager
from fastapi import FastAPI

from private_api.config import create_bucket, delete_bucket
from private_api.routes import router as minio_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_bucket()
    print("Bucket has been created")
    yield
    delete_bucket()
    print("Bucket has been deleted")


app = FastAPI(lifespan=lifespan)

app.include_router(minio_router)
