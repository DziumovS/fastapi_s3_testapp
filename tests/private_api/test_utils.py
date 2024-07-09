import pytest
from unittest.mock import MagicMock, Mock
from fastapi import HTTPException
from minio.error import S3Error

from private_api.utils import MinioUtils
from private_api.config import bucket_name


@pytest.mark.asyncio
async def test_upload_file_success(mock_minio_put_object, mock_minio_client, test_file_data):
    filename, file_data = test_file_data

    mock_minio_client.presigned_get_object = MagicMock(return_value="http://mocked_url")

    image_url = await MinioUtils.upload_file(filename, file_data)

    args, kwargs = mock_minio_put_object.call_args
    assert kwargs["bucket_name"] == bucket_name
    assert kwargs["object_name"] == filename
    assert kwargs["content_type"] == "application/octet-stream"
    assert kwargs["data"].read() == file_data
    assert kwargs["length"] == len(file_data)

    mock_minio_client.presigned_get_object.assert_called_once_with(
        bucket_name=bucket_name,
        object_name=filename
    )

    assert image_url == "http://mocked_url"


@pytest.mark.asyncio
@pytest.mark.parametrize("side_effect, expected_detail", [(S3Error(code="Mocked S3 error",
                                                                   message="Mocked S3 error message",
                                                                   resource="mocked_resource",
                                                                   request_id="mocked_request_id",
                                                                   host_id="mocked_host_id",
                                                                   response=Mock(status=500, data=b"Error response")),
                                                           "Error while working with MinIO"),
                                                          (Exception("Mocked generic error"),
                                                           "Internal server error")])
async def test_upload_file_errors(mock_minio_put_object, side_effect, expected_detail, test_file_data):
    filename, file_data = test_file_data

    mock_minio_put_object.side_effect = side_effect

    with pytest.raises(HTTPException) as excinfo:
        await MinioUtils.upload_file(filename, file_data)

    assert excinfo.value.status_code == 500
    assert expected_detail in excinfo.value.detail


@pytest.mark.asyncio
async def test_remove_file_success(mock_minio_remove_object, test_file_data):
    filename = test_file_data[0]

    result = await MinioUtils.remove_file(filename)

    mock_minio_remove_object.assert_called_once_with(bucket_name, filename)

    assert result == {"status": "success"}


@pytest.mark.asyncio
@pytest.mark.parametrize("side_effect, expected_detail", [(S3Error(code="Mocked S3 error",
                                                                   message="Mocked S3 error message",
                                                                   resource="mocked_resource",
                                                                   request_id="mocked_request_id",
                                                                   host_id="mocked_host_id",
                                                                   response=Mock(status=500, data=b"Error response")),
                                                           "Error while working with MinIO"),
                                                          (Exception("Mocked generic error"),
                                                           "Internal server error")])
async def test_remove_file_errors(mock_minio_remove_object, side_effect, expected_detail, test_file_data):
    filename = test_file_data[0]

    mock_minio_remove_object.side_effect = side_effect

    with pytest.raises(HTTPException) as excinfo:
        await MinioUtils.remove_file(filename)

    assert excinfo.value.status_code == 500
    assert expected_detail in excinfo.value.detail
