import os
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv


PATH_TO_ENV = Path(__file__).resolve().parent.parent.joinpath("private.env")
load_dotenv(PATH_TO_ENV)


client = Minio(
    endpoint=os.getenv("MINIO_URL"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=bool(int(os.getenv("SECURE")))
)

bucket_name = os.getenv("BUCKET_NAME")


def create_bucket():
    try:
        found = client.bucket_exists(bucket_name)
        if not found:
            client.make_bucket(bucket_name)

    except S3Error as err:
        print(f"Something went wrong while bucket creating: {err}")


def delete_bucket():
    try:
        found = client.bucket_exists(bucket_name)
        if found:
            objects = client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                client.remove_object(bucket_name, obj.object_name)
            client.remove_bucket(bucket_name)
        else:
            print(f"Bucket {bucket_name} does not exist")

    except S3Error as err:
        print(f"Something went wrong while bucket deleting: {err}")
