import io
from minio.error import S3Error
from fastapi import HTTPException

from private_api.config import client, bucket_name


class MinioUtils:
    @classmethod
    async def upload_file(cls, filename: str, file_data: bytes) -> str:
        try:
            client.put_object(
                bucket_name=bucket_name,
                object_name=filename,
                data=io.BytesIO(file_data),
                length=len(file_data),
                content_type="application/octet-stream"
            )
            image_url = client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=filename
            )
            return image_url

        except S3Error as err:
            raise HTTPException(status_code=500, detail=f"Error while working with MinIO: {str(err)}")
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(err)}")

    @classmethod
    async def remove_file(cls, filename: str):
        try:
            client.remove_object(bucket_name, filename)
            return {"status": "success"}

        except S3Error as err:
            raise HTTPException(status_code=500, detail=f"Error while working with MinIO: {str(err)}")
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(err)}")
