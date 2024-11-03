

from ..database import  mapping_process_collection
from app.domain.mapping.models import MappingsByJSONResponse,EditMappingRequest, MappingRequest
from app.repositories import mapping_repo
from app.domain.mapping.service import process_mapping

async def get_mappings_by_json_schema(json_schema_id: str):
    mappingJsons = []
    mapping_prosses_list = await mapping_repo.find_mappings_by_schema(json_schema_id)
    # TODO revisar cuales son todos los valores que necesitamos
    for mapping_process_doc in mapping_prosses_list:
        mappingByJSON = MappingsByJSONResponse(id=str(mapping_process_doc['_id']), name=mapping_process_doc['name'], jsonSchemaId=mapping_process_doc['jsonSchemaId'], mapping=mapping_process_doc['mapping'])
        mappingJsons.append(mappingByJSON)
    
    return mappingJsons


# ver si dejo esta
async def validate_and_update_mapping_process(request: MappingRequest, ontology, mapping_proccess_id: str):
    edit_body = EditMappingRequest(name=request.name, mapping=request.mapping)
    updated_result = await mapping_repo.update_mapping_process(edit_body, mapping_proccess_id, False)

    # here we validate if the mapping is correct
    status = process_mapping(request.mapping, ontology, request.jsonSchema)

    print("Update mapping proccess to be valid:", mapping_proccess_id)
    #updates the inserted mapping_process with the validation status
    updated_result = await mapping_repo.update_mapping_process(edit_body, mapping_proccess_id, True)
 
    return updated_result
