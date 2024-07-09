from contextlib import asynccontextmanager
from fastapi import FastAPI

from public_api.database.config import create_database, create_tables, delete_tables
from public_api.routes import router as memes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_database()
    await create_tables()
    print("Tables have been created")
    yield
    await delete_tables()
    print("Tables have been deleted")


app = FastAPI(lifespan=lifespan)

app.include_router(memes_router)
