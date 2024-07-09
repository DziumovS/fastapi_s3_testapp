import asyncpg
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from public_api.settings import DB_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_NAME
from public_api.database.models import Model


engine = create_async_engine(DB_URL, pool_size=50, max_overflow=0)
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_database():
    conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database="postgres"
    )

    databases = await conn.fetch("SELECT datname FROM pg_database")
    if POSTGRES_NAME not in [record["datname"] for record in databases]:
        await conn.execute(f'CREATE DATABASE {POSTGRES_NAME}')
        print(f"Database '{POSTGRES_NAME}' has been created.")

    await conn.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
