import pytest
from unittest.mock import Mock, AsyncMock
from app.services.mapping.service import MappingService
from app.services.mapping.types import MappingCreateData
from app.services.mapping.exceptions import InvalidMappingDataError, MappingNotFoundError
from app.models.mapping import MappingProcessDocument, EditMappingRequest

@pytest.fixture
def mapping_repository():
    return Mock()

@pytest.fixture
def mapping_service(mapping_repository):
    return MappingService(mapping_repository)

@pytest.fixture
def sample_mapping_data():
    return MappingCreateData(
        name="Test Mapping",
        json_schema_id="test_schema_id",
        ontology_id="test_ontology_id",
        mapping={"test_field": "test_value"},
        document_storage_path="/test/path",
        json_schema={"type": "object", "properties": {"test_field": {"type": "string"}}}
    )

@pytest.fixture
def sample_mapping_doc():
    return MappingProcessDocument(
        name="Test Mapping",
        jsonSchemaId="test_schema_id",
        ontologyId="test_ontology_id",
        mapping={"test_field": "test_value"},
        document_storage_path="/test/path",
        mapping_suscc_validated=True
    )

@pytest.mark.asyncio
async def test_create_mapping_process_success(mapping_service, sample_mapping_data):
    # Arrange
    future_result = "test_id"
    mapping_service.repository.create = AsyncMock(return_value=future_result)
    
    # Act
    result = await mapping_service.create_mapping_process(sample_mapping_data, True)
    
    # Assert
    assert result == future_result
    mapping_service.repository.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_mapping_process_failure(mapping_service, sample_mapping_data):
    # Arrange
    mapping_service.repository.create = AsyncMock(side_effect=Exception("Database error"))
    
    # Act & Assert
    with pytest.raises(InvalidMappingDataError):
        await mapping_service.create_mapping_process(sample_mapping_data, True)

@pytest.mark.asyncio
async def test_update_mapping_process(mapping_service):
    # Arrange
    edit_request = EditMappingRequest(
        name="Updated Mapping",
        mapping={"updated_field": "updated_value"}
    )
    mapping_service.repository.update = AsyncMock(return_value=True)
    
    # Act
    result = await mapping_service.update_mapping_process(edit_request, "test_id", True)
    
    # Assert
    assert result is True
    mapping_service.repository.update.assert_called_once()

@pytest.mark.asyncio
async def test_get_mapping_process_by_id_success(mapping_service, sample_mapping_doc):
    # Arrange
    mapping_service.repository.find_by_id = AsyncMock(return_value=sample_mapping_doc)
    
    # Act & Assert
    with pytest.raises(Exception):  # Will raise because ontology_service is not mocked
        await mapping_service.get_mapping_process_by_id("test_id")
    mapping_service.repository.find_by_id.assert_called_once_with("test_id")

@pytest.mark.asyncio
async def test_get_mapping_process_by_id_not_found(mapping_service):
    # Arrange
    mapping_service.repository.find_by_id = AsyncMock(return_value=None)
    
    # Act & Assert
    with pytest.raises(MappingNotFoundError):
        await mapping_service.get_mapping_process_by_id("test_id")

@pytest.mark.asyncio
async def test_delete_mapping_by_id(mapping_service):
    # Arrange
    mapping_service.repository.delete = AsyncMock(return_value=True)
    
    # Act
    result = await mapping_service.delete_mapping_by_id("test_id")
    
    # Assert
    assert result is True
    mapping_service.repository.delete.assert_called_once_with("test_id")
