from fastapi import APIRouter, Query, UploadFile, File, Form

from public_api.repository import MemeRepository
from public_api.schemas import MemeId, MemeBase, MemeFull, MemeDelete


router = APIRouter(
    prefix="/memes",
    tags=["Memes"],
)


@router.post("", response_model=MemeId)
async def create_meme(
        image: UploadFile = File(...),
        text: str = Form(...),
        meme_name: str = Form(...)
) -> MemeId:

    meme_data = MemeBase(text=text, meme_name=meme_name)
    result = await MemeRepository.create_meme(image=image, meme_data=meme_data)

    return result


@router.get("", response_model=list[MemeFull])
async def get_memes(
        limit: int = Query(default=5, lte=100),
        offset: int = Query(default=0)
) -> list[MemeFull]:
    return await MemeRepository.get_memes(offset=offset, limit=limit)


@router.get("/{meme_id}", response_model=MemeFull)
async def get_meme(meme_id: int) -> MemeFull:
    return await MemeRepository.get_meme(meme_id=meme_id)


@router.put("/{meme_id}")
async def update_meme(
        meme_id: int,
        image: UploadFile = File(None),
        text: str = Form(None),
        meme_name: str = Form(None)
) -> MemeFull | dict:
    if not any((image, text, meme_name)):
        return {"data": "Nothing to update"}

    meme_data = MemeBase(text=text, meme_name=meme_name)

    return await MemeRepository.update_meme(meme_id=meme_id, image=image, meme_data=meme_data)


@router.delete("/{meme_id}")
async def delete_meme(meme_id: int) -> MemeDelete:
    return await MemeRepository.delete_meme(meme_id=meme_id)
