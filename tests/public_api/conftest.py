import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import UploadFile


@pytest.fixture
def mock_upload_b_file():
    mock_file = MagicMock(spec=UploadFile)
    mock_file.read = AsyncMock(return_value=b"dummy_image_data")
    return mock_file


@pytest.fixture
def mock_upload_file():
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_image.jpg"
    return mock_file


@pytest.fixture
def mock_http_client():
    mock_client = MagicMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.fixture
def mock_successful_response():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"image_url": "http://example.com/image.jpg"})
    return mock_response


@pytest.fixture
def mock_failure_response():
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    return mock_response


@pytest.fixture()
def test_file_data() -> tuple:
    return "http://example.com/upload", "image.jpg", None


@pytest.fixture
def mock_get_image_url():
    with patch("public_api.repository.get_image_url") as mock:
        yield mock


@pytest.fixture
def mock_new_session():
    with patch("public_api.repository.new_session", autospec=True) as mock:
        yield mock


@pytest.fixture
def mock_meme_model():
    with patch("public_api.repository.Memes", autospec=True) as mock:
        yield mock


