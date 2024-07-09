from fastapi import APIRouter
from pydantic import HttpUrl

from private_api.repository import MinioRepository
from private_api.schemas import UploadRequest, UpdateRequest


router = APIRouter(
    tags=["Memes"],
)


@router.post("/")
async def create_meme(request: UploadRequest) -> HttpUrl:
    return await MinioRepository.create_meme(request)


@router.delete("/{filename}")
async def delete_meme(filename: str) -> dict:
    return await MinioRepository.delete_meme(filename)


@router.put("/")
async def update_meme(request: UpdateRequest) -> HttpUrl:
    return await MinioRepository.update_meme(request)
