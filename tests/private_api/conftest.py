import pytest
import base64
from unittest.mock import patch, MagicMock

from private_api.schemas import UploadRequest, UpdateRequest


@pytest.fixture(autouse=True)
def mock_minio_client() -> MagicMock:
    with patch("private_api.utils.client", new_callable=MagicMock) as mock_client:
        yield mock_client


@pytest.fixture(autouse=True)
def mock_bucket_setup_teardown() -> MagicMock:
    with patch("private_api.config.create_bucket", MagicMock()):
        with patch("private_api.config.delete_bucket", MagicMock()):
            yield


@pytest.fixture()
def mock_minio_put_object(mock_minio_client: MagicMock) -> MagicMock:
    mock_minio_client.put_object = MagicMock()
    yield mock_minio_client.put_object


@pytest.fixture()
def mock_minio_remove_object(mock_minio_client: MagicMock) -> MagicMock:
    mock_minio_client.remove_object = MagicMock()
    yield mock_minio_client.remove_object


@pytest.fixture()
def test_file_data() -> tuple:
    return "test_file.txt", b"test data"


@pytest.fixture
def mock_upload_request() -> UploadRequest:
    image_base64 = base64.b64encode(b"test_image_data").decode("utf-8")
    return UploadRequest(filename="test.jpg", image=image_base64)


@pytest.fixture
def mock_update_request() -> UpdateRequest:
    image_base64 = base64.b64encode(b"test_image_data").decode("utf-8")
    return UpdateRequest(old_filename="old.jpg", filename="new.jpg", image=image_base64)
