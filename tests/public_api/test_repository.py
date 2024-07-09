import datetime
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from public_api.repository import MemeRepository, Memes
from public_api.schemas import MemeBase, MemeId, MemeFull
from public_api.settings import PRIVATE_SERVICE_URL


@pytest.mark.asyncio
async def test_create_meme_success(mock_get_image_url, mock_new_session, mock_meme_model, mock_upload_file):
    mock_meme_data = MemeBase(meme_name="Test Meme", text="This is a test meme")

    mock_image_url = "http://mocked-url.com/image.jpg"
    mock_get_image_url.return_value = mock_image_url

    mock_session_instance = MagicMock()
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    mock_new_meme_instance = MagicMock()
    mock_new_meme_instance.id = 1
    mock_new_meme_instance.meme_name = mock_meme_data.meme_name
    mock_new_meme_instance.image_url = mock_image_url
    mock_new_meme_instance.text = mock_meme_data.text
    mock_meme_model.return_value = mock_new_meme_instance

    result = await MemeRepository.create_meme(mock_upload_file, mock_meme_data)

    assert isinstance(result, MemeId)
    assert result.id == mock_new_meme_instance.id
    assert result.meme_name == mock_meme_data.meme_name
    assert result.image_url == mock_image_url
    assert result.text == mock_meme_data.text
    mock_get_image_url.assert_called_once_with(url=PRIVATE_SERVICE_URL, image=mock_upload_file,
                                               filename=mock_upload_file.filename)
    mock_meme_model.assert_called_once_with(
        meme_name=mock_meme_data.meme_name,
        filename=mock_upload_file.filename,
        text=mock_meme_data.text,
        image_url=mock_image_url
    )
    mock_session_instance.add.assert_called_once_with(mock_new_meme_instance)


@pytest.mark.asyncio
async def test_create_meme_error(mock_get_image_url, mock_new_session, mock_meme_model, mock_upload_file):
    mock_meme_data = MemeBase(meme_name="Test Meme", text="This is a test meme")

    mock_get_image_url.side_effect = Exception("Image processing error")

    mock_session_instance = MagicMock()
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    with pytest.raises(HTTPException) as exc_info:
        await MemeRepository.create_meme(mock_upload_file, mock_meme_data)

    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Meme creation error"
    mock_get_image_url.assert_called_once_with(url=PRIVATE_SERVICE_URL, image=mock_upload_file,
                                               filename=mock_upload_file.filename)
    mock_meme_model.assert_not_called()
    mock_session_instance.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_memes_success(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    mock_meme_instances = [
        Memes(id=1, meme_name="Test Meme 1", filename="image1.jpg", image_url="http://example.com/image1.jpg",
              text="Text 1", date_added=datetime.datetime.now(), date_updated=datetime.datetime.now()),
        Memes(id=2, meme_name="Test Meme 2", filename="image2.jpg", image_url="http://example.com/image2.jpg",
              text="Text 2", date_added=datetime.datetime.now(), date_updated=datetime.datetime.now()),
    ]

    mock_query_result = MagicMock()
    mock_query_result.scalars().all.return_value = mock_meme_instances

    mock_session_instance.execute.return_value = mock_query_result

    offset = 0
    limit = 10
    result = await MemeRepository.get_memes(offset, limit)

    assert isinstance(result, list)
    assert len(result) == len(mock_meme_instances)

    for meme in result:
        assert isinstance(meme, MemeFull)
        assert meme.meme_name in ["Test Meme 1", "Test Meme 2"]
        assert meme.image_url in ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
        assert meme.text in ["Text 1", "Text 2"]

    query = select(Memes).offset(offset).limit(limit)

    assert mock_session_instance.execute.call_count == 1
    called_args, _ = mock_session_instance.execute.call_args
    assert isinstance(called_args[0], type(query))
    assert called_args[0].compile().params == query.compile().params


@pytest.mark.asyncio
async def test_get_memes_error_handling(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    offset = 0
    limit = 10
    mock_session_instance.execute.side_effect = Exception("Database connection error")

    with pytest.raises(HTTPException) as exc_info:
        await MemeRepository.get_memes(offset, limit)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error getting the list of memes"

    mock_session_instance.execute.assert_called_once()
    actual_query = mock_session_instance.execute.call_args[0][0]
    expected_query = select(Memes).offset(offset).limit(limit)
    assert str(actual_query) == str(expected_query)


@pytest.mark.asyncio
async def test_get_meme_success(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    meme_id = 1
    mock_meme = Memes(id=meme_id, meme_name="Test Meme", filename="image.jpg", image_url="http://example.com/image.jpg",
                      text="Test Text", date_added=datetime.datetime.now(), date_updated=datetime.datetime.now())

    mock_session_instance.get.return_value = mock_meme

    result = await MemeRepository.get_meme(meme_id)

    assert isinstance(result, Memes)
    assert result.id == meme_id
    assert result.meme_name == "Test Meme"

    mock_session_instance.get.assert_called_once_with(Memes, meme_id)


@pytest.mark.asyncio
async def test_get_meme_not_found(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    meme_id = 10
    mock_session_instance.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await MemeRepository.get_meme(meme_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Meme not found"

    mock_session_instance.get.assert_called_once_with(Memes, meme_id)


@pytest.mark.asyncio
async def test_get_meme_error(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    meme_id = 1
    mock_session_instance.get.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await MemeRepository.get_meme(meme_id)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Meme retrieval error"

    mock_session_instance.get.assert_called_once_with(Memes, meme_id)


@pytest.mark.asyncio
async def test_update_meme_success(mock_new_session, mock_upload_file, mock_get_image_url, mock_meme_model):
    meme_id = 1
    mock_meme_data = MemeBase(meme_name="Updated Test Meme", text="This is an updated test meme")
    mock_image_url = "http://mocked-url.com/updated_image.jpg"
    mock_get_image_url.return_value = mock_image_url

    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance
    mock_meme_instance = Memes(
        id=1, meme_name="Test Meme 1", filename="image1.jpg", image_url="http://example.com/image1.jpg", text="Text 1",
        date_added=datetime.datetime.now(), date_updated=datetime.datetime.now())
    mock_session_instance.get.return_value = mock_meme_instance

    mock_upload_file.filename = "updated_test_image.jpg"

    updated_meme = await MemeRepository.update_meme(meme_id, mock_upload_file, mock_meme_data)

    mock_meme_instance.filename = mock_upload_file.filename
    mock_meme_instance.old_filename = "image1.jpg"

    mock_get_image_url.assert_called_once_with(
        url=PRIVATE_SERVICE_URL,
        image=mock_upload_file,
        filename=mock_upload_file.filename,
        old_filename="image1.jpg"
    )
    mock_session_instance.add.assert_called_once_with(mock_meme_instance)
    mock_session_instance.commit.assert_called_once()

    assert updated_meme.meme_name == "Updated Test Meme"
    assert updated_meme.image_url == mock_image_url


@pytest.mark.asyncio
async def test_update_meme_not_found(mock_new_session, mock_upload_file, mock_get_image_url, mock_meme_model):
    meme_id = 1
    mock_meme_data = MemeBase(meme_name="Updated Test Meme", text="This is an updated test meme")

    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance
    mock_session_instance.get.return_value = None

    with pytest.raises(HTTPException):
        await MemeRepository.update_meme(meme_id, mock_upload_file, mock_meme_data)


@pytest.mark.asyncio
async def test_update_meme_image_error(mock_new_session, mock_upload_file, mock_get_image_url, mock_meme_model):
    meme_id = 1
    mock_meme_data = MemeBase(meme_name="Updated Test Meme", text="This is an updated test meme")

    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance
    mock_meme_instance = Memes(
        id=1, meme_name="Test Meme 1", filename="image1.jpg", image_url="http://example.com/image1.jpg", text="Text 1",
        date_added=datetime.datetime.now(), date_updated=datetime.datetime.now())
    mock_session_instance.get.return_value = mock_meme_instance

    mock_upload_file.filename = "updated_test_image.jpg"
    mock_upload_file.read.side_effect = IOError("Unable to read uploaded file")

    with pytest.raises(HTTPException):
        await MemeRepository.update_meme(meme_id, mock_upload_file, mock_meme_data)


@pytest.mark.asyncio
async def test_delete_meme_success(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    meme_id = 1
    meme = Memes(id=meme_id, meme_name="Test Meme", filename="test_image.jpg", date_added=datetime.datetime.now(),
                 date_updated=datetime.datetime.now())
    mock_session_instance.get.return_value = meme

    with patch("public_api.repository.delete_object", return_value=True) as mock_delete_object:
        result = await MemeRepository.delete_meme(meme_id)

        assert result == meme
        mock_session_instance.get.assert_called_once_with(Memes, meme_id)
        mock_delete_object.assert_called_once_with(url=f"{PRIVATE_SERVICE_URL}/test_image.jpg")
        mock_session_instance.delete.assert_called_once_with(meme)
        mock_session_instance.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_meme_not_found(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance
    meme_id = 1
    mock_session_instance.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await MemeRepository.delete_meme(meme_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Meme not found"
    mock_session_instance.get.assert_called_once_with(Memes, meme_id)


@pytest.mark.asyncio
async def test_delete_meme_file_deletion_error(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    meme_id = 1
    meme = Memes(id=meme_id, meme_name="Test Meme", filename="test_image.jpg", date_added=datetime.datetime.now(),
                 date_updated=datetime.datetime.now())
    mock_session_instance.get.return_value = meme

    with patch("public_api.repository.delete_object",
               side_effect=HTTPException(status_code=500, detail="File deletion error")) as mock_delete_object:
        with pytest.raises(HTTPException) as exc_info:
            await MemeRepository.delete_meme(meme_id)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Meme deletion error: File deletion error"
        mock_session_instance.get.assert_called_once_with(Memes, meme_id)
        mock_delete_object.assert_called_once_with(url=f"{PRIVATE_SERVICE_URL}/test_image.jpg")
        mock_session_instance.delete.assert_not_called()
        mock_session_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_meme_db_error(mock_new_session):
    mock_session_instance = MagicMock(spec=AsyncSession)
    mock_new_session.return_value.__aenter__.return_value = mock_session_instance

    meme_id = 1
    meme = Memes(id=meme_id, meme_name="Test Meme", filename="test_image.jpg", date_added=datetime.datetime.now(),
                 date_updated=datetime.datetime.now())
    mock_session_instance.get.return_value = meme

    with patch("public_api.repository.delete_object", return_value=True):
        mock_session_instance.delete.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await MemeRepository.delete_meme(meme_id)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "An unexpected error occurred while deleting the meme"
        mock_session_instance.get.assert_called_once_with(Memes, meme_id)
        mock_session_instance.delete.assert_called_once_with(meme)
        mock_session_instance.commit.assert_not_called()
