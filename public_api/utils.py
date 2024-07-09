import base64
import httpx
from fastapi import UploadFile, HTTPException


async def get_image_url(url: str, image: UploadFile, filename: str, old_filename: str = None) -> str:
    file_data = await image.read()
    encoded_file_data = base64.b64encode(file_data).decode("utf-8")

    data = {
        "image": encoded_file_data,
        "filename": filename,
        "old_filename": old_filename
    }

    async with httpx.AsyncClient() as client:
        method = client.put if old_filename else client.post
        response = await method(url=url, json=data)

        if response.status_code == 200:
            image_url = response.json()

            return image_url

        else:
            error_message = f"Error {response.status_code}: {response.text}"
            raise HTTPException(status_code=response.status_code, detail=error_message)


async def delete_object(url: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(url=url)

        if response.status_code == 200:
            return True
        else:
            error_message = f"Error {response.status_code}: {response.text}"
            raise HTTPException(status_code=response.status_code, detail=error_message)
