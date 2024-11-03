

from ..database import  mapping_process_collection
from app.domain.mapping.models import MappingProcessDocument, MappingsByJSONResponse,EditMappingRequest, MappingRequest
from app.repositories import mapping_repo, schema_repo, ontology_repo
from app.domain.mapping.service import process_mapping
from app.services import ontology_service as onto_service
from bson import ObjectId

async def get_mappings_by_json_schema(json_schema_id: str):
    mappingJsons = []
    mapping_prosses_list = await mapping_repo.find_mappings_by_schema(json_schema_id)
    # TODO revisar cuales son todos los valores que necesitamos
    for mapping_process_doc in mapping_prosses_list:
        mappingByJSON = MappingsByJSONResponse(id=str(mapping_process_doc['_id']), name=mapping_process_doc['name'], jsonSchemaId=mapping_process_doc['jsonSchemaId'], mapping=mapping_process_doc['mapping'])
        mappingJsons.append(mappingByJSON)
    
    return mappingJsons

def build_update_data_from_mapping_request(edit_mapping_request: EditMappingRequest):
    update_data ={}
    for key, value in edit_mapping_request:
            if value is not None and value != "" and value != {} and value != "string":
                update_data[key] = value
    return update_data

async def update_mapping_process(request: MappingRequest, ontology, mapping_proccess_id: str):
    edit_body = EditMappingRequest(name=request.name, mapping=request.mapping)
    data_to_update = build_update_data_from_mapping_request(edit_body)
    updated_result = await mapping_repo.update_mapping_process(data_to_update, mapping_proccess_id, False)

    return updated_result

# validate_and_save_mapping_process validates the rules and saves a mapping process
async def validate_and_save_mapping_process(request: MappingRequest, mapping_proccess_id: str, ontology_id: str):
    ontology = await onto_service.get_ontology_by_id(ontology_id)
    # return ontology not found

    if (mapping_proccess_id is not None):
        print("about to EDIT!!")
        result = await update_mapping_process(request, ontology, mapping_proccess_id) #ver si se levanta la excepcion de validacion correctamente
    else : 
        print("about to SAVE!!")
        schema_id = await schema_repo.insert_schema(request.jsonSchema)
        mapping_process_docu = MappingProcessDocument(name=request.name, mapping=request.mapping,
                                                        ontologyId=ontology_id,
                                                        jsonSchemaId=str(schema_id),
                                                        mapping_suscc_validated=False)
        mapping_process_id_inserted = await mapping_repo.insert_mapping_process(mapping_process_docu)
  
    status = process_mapping(request.mapping, ontology, request.jsonSchema)
    print("status", status)
    updated_result = await mapping_repo.update_mapping_process({}, str(mapping_process_id_inserted), True)

    return mapping_process_id_inserted