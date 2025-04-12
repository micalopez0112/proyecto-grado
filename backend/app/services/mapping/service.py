from app.repositories.mapping.repository import MappingRepository
from app.models.mapping import MappingProcessDocument, MappingsByJSONResponse, EditMappingRequest, MappingRequest, PutMappingRequest
from app.services.schema.service import SchemaService
from app.services.schema.types import SchemaCreateData
from app.services.ontology.service import OntologyService
from app.rules_validation.mapping_rules import validate_mapping, get_json_schema_property_type
from app.services.ontology.types import build_ontology_response
from .types import build_mapping_id_name_tupple, MappingBasicInfo, build_mapping_proccess_response,build_update_data_from_mapping_request, MappingCreateData, MappingUpdateData
from .exceptions import MappingNotFoundError, InvalidMappingDataError,MappingValidationError

class MappingService:
    def __init__(self, mapping_repository: MappingRepository, ontology_service: OntologyService, schema_service: SchemaService):
        self.repository = mapping_repository
        self.ontology_service = ontology_service
        self.schema_service = schema_service

    async def create_mapping_process(self, mapping_create_data: MappingCreateData, validated: bool) -> str:
        """
        Create a new mapping process.
        
        Args:
            data: The mapping data to create
            
        Returns:
            str: The ID of the created mapping
            
        Raises:
            MappingValidationError: If the mapping fails validation
            InvalidMappingDataError: If the data is invalid
        """
        try:
            # Create mapping document
            mapping_doc = MappingProcessDocument(
                name=mapping_create_data.name,
                jsonSchemaId=str(mapping_create_data.json_schema_id),
                ontologyId=mapping_create_data.ontology_id,
                mapping=mapping_create_data.mapping,
                document_storage_path=mapping_create_data.document_storage_path,
                mapping_suscc_validated=validated
            )

            # Save to repository
            mapping_id = await self.repository.create(mapping_doc)
            return mapping_id
        except Exception as e:
            raise InvalidMappingDataError(f"Could not create mapping: {str(e)}")

    async def update_mapping_process(self, edit_mapping_request: EditMappingRequest, mapping_proccess_id: str, mapping_validated: bool):
        data_to_update = build_update_data_from_mapping_request(edit_mapping_request)
        updated_result = await self.repository.update(mapping_proccess_id, data_to_update, mapping_validated)

        return updated_result

    # TODO: completar
    async def create_or_update_mapping_process(self, mapping_create_data: MappingCreateData, mapping_proccess_id: str):
        try:
            schema_id = await self.schema_service.get_or_create_schema(SchemaCreateData(
                collection_path=mapping_create_data.document_storage_path,
                json_schema=mapping_create_data.json_schema,
                schema_id=mapping_create_data.json_schema_id
            ))
            print("JUST GOT SCHEMA FROM NEW ARQ")
            if mapping_proccess_id is not None and mapping_proccess_id != "":
                edit_body = EditMappingRequest(name=mapping_create_data.name, mapping=mapping_create_data.mapping)
                mapping_updated = await self.update_mapping_process(edit_body, mapping_proccess_id, False)
                mapping_id = mapping_proccess_id
            else:
                mapping_create_data.json_schema_id = schema_id
                mapping_id = await self.create_mapping_process(mapping_create_data, False)
            
            return mapping_id, schema_id
        except Exception as e:
            print(e)
            raise InvalidMappingDataError(f"Could not create or update mapping: {str(e)}")

    # Revisar
    async def create_or_update_mapping_process_with_validation(self, mapping_create_data: MappingCreateData, mapping_proccess_id: str):
        try:
            mapping_id, schema_id = await self.create_or_update_mapping_process(mapping_create_data, mapping_proccess_id)
            jsonSchema = mapping_create_data.json_schema
            jsonSchema['_id'] = schema_id

            ontology = await self.ontology_service.get_ontology_by_id(mapping_create_data.ontology_id)
            # all mapping rules are validated here
            status = validate_mapping(mapping_create_data.mapping, ontology, jsonSchema)
            updated = await self.update_mapping_process(EditMappingRequest(name=mapping_create_data.name, mapping=mapping_create_data.mapping), mapping_id, True)
            
            return mapping_id
        except ValueError as e:
            raise e
        except Exception as e:
            print(e)
            raise InvalidMappingDataError(f"Could not create or update mapping: {str(e)}")

    async def get_mappings_by_json_schema(self, json_schema_id: str):
        mappingJsons = []
        mapping_prosses_list = await self.repository.find_mappings_by_schema(json_schema_id, True)
        for mapping_process_doc in mapping_prosses_list:
            mappingByJSON = MappingsByJSONResponse(idMapping=str(mapping_process_doc['_id']), name=mapping_process_doc['name'], jsonSchemaId=mapping_process_doc['jsonSchemaId'])
            mappingJsons.append(mappingByJSON)
        
        return mappingJsons

    async def get_mappings(self, validated_mappings: bool = None) :
        """Get all mappings with optional validation filter.
        
        Args:
            validated_mappings: Optional filter for validated mappings
            
        Returns:
            List[MappingBasicInfo]: List of mappings with basic information
        """
        query = {}
        if validated_mappings is not None and validated_mappings is True:
            query = {'mapping_suscc_validated': validated_mappings}

        projection = {'_id': 1, 'name': 1}  
        mapping_process_docs_list = await self.repository.find_by_query(query, projection)

        return [
            MappingBasicInfo(id=str(doc['_id']), name=doc['name'])
            for doc in mapping_process_docs_list
        ]

    async def get_mapping_process_by_id(self, mapping_process_id: str, filter_dp: bool = None):
        try:
            """Get a mapping process by ID with optional data property filtering."""
            mapping_process_doc = await self.repository.find_by_id(mapping_process_id)
            if not mapping_process_doc:
                raise MappingNotFoundError(f"Mapping {mapping_process_id} not found")

            if filter_dp:
                # Filter mapping to retrieve only data properties components
                mapping_process_doc.mapping = {
                    k: v for k, v in mapping_process_doc.mapping.items() 
                    if get_json_schema_property_type(k) != ""
                }
            
            onto_id = mapping_process_doc.ontologyId
            ontology = await self.ontology_service.get_ontology_by_id(onto_id)
            ontology_data = build_ontology_response(ontology, onto_id)
            
            print("#Ontology data before return getMapping#: ", ontology_data)
            JSON_schema = await self.schema_service.get_schema_by_id(mapping_process_doc.jsonSchemaId)
            complete_mapping = build_mapping_proccess_response(ontology_data, JSON_schema, mapping_process_doc.mapping, mapping_process_doc)
            
            return complete_mapping
        except Exception as e:
            print("Error getting mapping process:", e)
            raise InvalidMappingDataError(f"Could not get mapping process: {str(e)}")
    
    async def delete_mapping_by_id(self, mapping_process_id: str):
        return await self.repository.delete(mapping_process_id)