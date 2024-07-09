import pytest
from unittest.mock import patch
from fastapi import HTTPException

from private_api.repository import MinioRepository


@patch("private_api.repository.MinioUtils", autospec=True)
class TestMinioRepository:
    @pytest.mark.asyncio
    async def test_create_meme(self, MockMinioUtils, mock_upload_request):
        MockMinioUtils.upload_file.return_value = "http://mocked-url"
        result = await MinioRepository.create_meme(mock_upload_request)
        assert result == "http://mocked-url"

    @pytest.mark.asyncio
    async def test_delete_meme(self, MockMinioUtils):
        MockMinioUtils.remove_file.return_value = {"status": "success"}
        result = await MinioRepository.delete_meme("test.jpg")
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_update_meme_success(self, MockMinioUtils, mock_update_request):
        MockMinioUtils.upload_file.return_value = "http://mocked-new-url"
        MockMinioUtils.remove_file.return_value = {"status": "success"}

        result = await MinioRepository.update_meme(mock_update_request)
        assert result == "http://mocked-new-url"

    @pytest.mark.asyncio
    async def test_update_meme_failure_delete(self, MockMinioUtils, mock_update_request):
        MockMinioUtils.upload_file.return_value = "http://mocked-new-url"
        MockMinioUtils.remove_file.return_value = {"status": "failed"}

        with pytest.raises(HTTPException):
            await MinioRepository.update_meme(mock_update_request)

    @pytest.mark.asyncio
    async def test_update_meme_failure_upload(self, MockMinioUtils, mock_update_request):
        MockMinioUtils.upload_file.side_effect = Exception("Upload failed")

        with pytest.raises(HTTPException):
            await MinioRepository.update_meme(mock_update_request)

    @pytest.mark.asyncio
    async def test_update_meme_http_exception(self, MockMinioUtils, mock_update_request):
        MockMinioUtils.upload_file.side_effect = HTTPException(status_code=400, detail="Bad Request")

        with pytest.raises(HTTPException):
            await MinioRepository.update_meme(mock_update_request)
