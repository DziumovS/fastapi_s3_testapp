import base64
from fastapi import HTTPException

from private_api.schemas import UploadRequest, UpdateRequest
from private_api.utils import MinioUtils


class MinioRepository:
    @classmethod
    async def create_meme(cls, request: UploadRequest):
        file_data = base64.b64decode(request.image)
        return await MinioUtils.upload_file(request.filename, file_data)

    @classmethod
    async def delete_meme(cls, filename: str):
        return await MinioUtils.remove_file(filename)

    @classmethod
    async def update_meme(cls, request: UpdateRequest):
        try:
            new_file_url = await cls.create_meme(
                UploadRequest(filename=request.filename, image=request.image)
            )

            delete_response = await cls.delete_meme(request.old_filename)

            if delete_response["status"] != "success":
                await cls.delete_meme(request.filename)
                raise HTTPException(status_code=500, detail="Failed to delete the old object")

            return new_file_url

        except HTTPException as http_err:
            raise http_err
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(err)}")
