from fastapi import HTTPException
from pydantic import BaseModel, field_validator
import base64


class UploadRequest(BaseModel):
    filename: str
    image: str

    @field_validator("image")
    def validate_image(cls, value):
        try:
            base64.b64decode(value)
            return value
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid base64 encoded image")


class UpdateRequest(UploadRequest):
    old_filename: str
