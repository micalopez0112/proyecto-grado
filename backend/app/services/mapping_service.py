

from ..database import  mapping_process_collection
from app.domain.mapping.models import MappingsByJSONResponse
from app.repositories import mapping_repo

async def get_mappings_by_json_schemV1(json_schema_id: str):
    mappingJsons = []
    mapping_prosses_list = await mapping_repo.find_mappings_by_schema(json_schema_id)
    # TODO revisar cuales son todos los valores que necesitamos
    for mapping_process_doc in mapping_prosses_list:
        mappingByJSON = MappingsByJSONResponse(id=str(mapping_process_doc['_id']), name=mapping_process_doc['name'], jsonSchemaId=mapping_process_doc['jsonSchemaId'], mapping=mapping_process_doc['mapping'])
        mappingJsons.append(mappingByJSON)
    
    return mappingJsons