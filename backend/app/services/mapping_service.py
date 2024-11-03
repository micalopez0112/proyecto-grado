

from ..database import  mapping_process_collection
from app.domain.mapping.models import MappingsByJSONResponse

async def get_mappings_by_json_schemV1(json_schema_id: str):
    cursor = mapping_process_collection.find({'jsonSchemaId': json_schema_id})
    mapping_process_docs = await cursor.to_list(length=None)
    mappingJsons = []
    # TODO revisar cuales son todos los valores que necesitamos
    for mapping_process_doc in mapping_process_docs:
        mappingByJSON = MappingsByJSONResponse(id=str(mapping_process_doc['_id']), name=mapping_process_doc['name'], jsonSchemaId=mapping_process_doc['jsonSchemaId'], mapping=mapping_process_doc['mapping'])
        mappingJsons.append(mappingByJSON)
    
    return mappingJsons