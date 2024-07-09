import pytest
import httpx
import base64
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException

from public_api.utils import get_image_url, delete_object


@pytest.mark.asyncio
async def test_get_image_url_success(mock_upload_b_file, mock_http_client, mock_successful_response, test_file_data):
    mock_http_client.post = AsyncMock(return_value=mock_successful_response)
    httpx.AsyncClient = MagicMock(return_value=mock_http_client)

    url, filename, old_filename = test_file_data

    image_url = await get_image_url(url, mock_upload_b_file, filename, old_filename)

    assert image_url == {"image_url": "http://example.com/image.jpg"}
    mock_upload_b_file.read.assert_called_once()
    mock_http_client.post.assert_called_once_with(url=url, json={
        "image": base64.b64encode(b"dummy_image_data").decode("utf-8"),
        "filename": filename,
        "old_filename": old_filename
    })


@pytest.mark.asyncio
async def test_get_image_url_failure(mock_upload_b_file, mock_http_client, mock_failure_response, test_file_data):
    mock_http_client.post = AsyncMock(return_value=mock_failure_response)
    httpx.AsyncClient = MagicMock(return_value=mock_http_client)

    url, filename, old_filename = test_file_data

    with pytest.raises(HTTPException) as exc_info:
        await get_image_url(url, mock_upload_b_file, filename, old_filename)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Error 404: Not Found"
    mock_upload_b_file.read.assert_called_once()
    mock_http_client.post.assert_called_once_with(url=url, json={
        "image": base64.b64encode(b"dummy_image_data").decode("utf-8"),
        "filename": filename,
        "old_filename": old_filename
    })


@pytest.mark.asyncio
async def test_delete_object_success(mock_http_client, mock_successful_response):
    url = "http://example.com/delete"

    mock_http_client.delete = AsyncMock(return_value=mock_successful_response)
    httpx.AsyncClient = MagicMock(return_value=mock_http_client)

    result = await delete_object(url)

    assert result is True
    mock_http_client.delete.assert_called_once_with(url=url)


@pytest.mark.asyncio
async def test_delete_object_failure(mock_http_client, mock_failure_response):
    url = "http://example.com/delete"

    mock_http_client.delete = AsyncMock(return_value=mock_failure_response)
    httpx.AsyncClient = MagicMock(return_value=mock_http_client)

    with pytest.raises(HTTPException) as exc_info:
        await delete_object(url)

    assert exc_info.value.status_code == 404
    assert str(exc_info.value.detail) == "Error 404: Not Found"
    mock_http_client.delete.assert_called_once_with(url=url)
