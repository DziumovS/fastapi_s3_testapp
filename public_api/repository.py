from typing import Optional
from sqlalchemy import select
from fastapi import HTTPException, UploadFile

from public_api.database.config import new_session
from public_api.database.models import Memes
from public_api.schemas import MemeId, MemeBase, MemeFull, MemeDelete
from public_api.utils import get_image_url, delete_object
from public_api.settings import PRIVATE_SERVICE_URL


class MemeRepository:
    @classmethod
    async def create_meme(cls, image: UploadFile, meme_data: MemeBase) -> MemeId:
        try:
            filename = image.filename

            image_url = await get_image_url(
                url=PRIVATE_SERVICE_URL,
                image=image,
                filename=filename
            )

            async with new_session() as session:
                async with session.begin():
                    new_meme = Memes(
                        meme_name=meme_data.meme_name,
                        filename=filename,
                        text=meme_data.text,
                        image_url=image_url
                    )
                    session.add(new_meme)

            return MemeId(
                id=new_meme.id,
                meme_name=new_meme.meme_name,
                image_url=new_meme.image_url,
                text=new_meme.text
            )

        except Exception as err:
            raise HTTPException(status_code=500, detail="Meme creation error")

    @classmethod
    async def get_memes(cls, offset: int, limit: int) -> list[MemeFull]:
        async with new_session() as session:
            try:
                query = select(Memes).offset(offset).limit(limit)
                result = await session.execute(query)
                meme_models = result.scalars().all()
                return [MemeFull.from_orm(meme_model) for meme_model in meme_models]

            except Exception as err:
                raise HTTPException(status_code=500, detail="Error getting the list of memes")

    @classmethod
    async def get_meme(cls, meme_id: int) -> MemeFull:
        async with new_session() as session:
            try:
                meme = await session.get(Memes, meme_id)
                if not meme:
                    raise HTTPException(status_code=404, detail="Meme not found")
                return meme

            except HTTPException:
                raise
            except Exception as err:
                raise HTTPException(status_code=500, detail="Meme retrieval error")

    @classmethod
    async def update_meme(cls, meme_id: int, image: Optional[UploadFile], meme_data: MemeBase) -> MemeFull:
        async with new_session() as session:
            async with session.begin():
                try:
                    meme_model = await session.get(Memes, meme_id)
                    if not meme_model:
                        raise HTTPException(status_code=404, detail="Meme not found")

                    update_data = meme_data.dict(exclude_unset=True)

                    if image is not None:
                        filename = image.filename
                        old_filename = meme_model.filename

                        image_url = await get_image_url(
                            url=PRIVATE_SERVICE_URL,
                            image=image,
                            filename=filename,
                            old_filename=old_filename
                        )

                        update_data.update({
                                "filename": filename,
                                "image_url": image_url
                        })

                    for key, value in update_data.items():
                        if value is not None:
                            setattr(meme_model, key, value)

                    session.add(meme_model)
                    await session.commit()

                    return MemeFull.from_orm(meme_model)

                except HTTPException as err:
                    raise
                except Exception as err:
                    raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")

    @classmethod
    async def delete_meme(cls, meme_id: int) -> MemeDelete:
        async with new_session() as session:
            async with session.begin():
                meme = await session.get(Memes, meme_id)
                if not meme:
                    raise HTTPException(status_code=404, detail="Meme not found")

                filename = meme.filename

                try:
                    await delete_object(url=f"{PRIVATE_SERVICE_URL}/{filename}")
                    await session.delete(meme)
                    await session.commit()
                    return meme

                except HTTPException as err:
                    raise HTTPException(status_code=500, detail=f"Meme deletion error: {err.detail}")
                except Exception as err:
                    raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the meme")
