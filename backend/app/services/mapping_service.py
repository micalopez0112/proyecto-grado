

from ..database import  mapping_process_collection, DLzone
from app.models.mapping import MappingProcessDocument, MappingsByJSONResponse,EditMappingRequest, MappingRequest, PutMappingRequest
from app.repositories import mapping_repo, metadata_repo
from app.rules_validation.mapping_rules import validate_mapping, getJsonSchemaPropertieType
from app.services import ontology_service as onto_service
from app.services import schema_service as schema_service
from app.dq_evaluation.evaluation import find_json_keys

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

async def update_mapping_process(request: MappingRequest, mapping_proccess_id: str, mapping_validated: bool):
    edit_body = EditMappingRequest(name=request.name, mapping=request.mapping)
    data_to_update = build_update_data_from_mapping_request(edit_body)
    updated_result = await mapping_repo.update_mapping_process(data_to_update, mapping_proccess_id, mapping_validated)

    return updated_result

# validate_and_save_mapping_process validates the rules and saves a mapping process
async def validate_and_save_mapping_process(request: MappingRequest, mapping_proccess_id: str, ontology_id: str):
    ontology = await onto_service.get_ontology_by_id(ontology_id)
    # return ontology not found
    if (mapping_proccess_id is not None and mapping_proccess_id != ""):
        result = await update_mapping_process(request, mapping_proccess_id, False) #ver si se levanta la excepcion de validacion correctamente
        mapping_id = mapping_proccess_id
    else : 
        full_collection_path = DLzone + request.documentStoragePath
        schema_id = await schema_service.get_or_create_schema(full_collection_path,request.jsonSchema)
        mapping_process_docu = MappingProcessDocument(name=request.name, mapping=request.mapping, ontologyId=ontology_id,
                                                        jsonSchemaId=str(schema_id),
                                                        document_storage_path = full_collection_path,
                                                        mapping_suscc_validated=False)
        mapping_process_id_inserted = await mapping_repo.insert_mapping_process(mapping_process_docu)
        mapping_id = mapping_process_id_inserted

    status = validate_mapping(request.mapping, ontology, request.jsonSchema)
    updated_result = await mapping_repo.update_mapping_process({}, str(mapping_id), True)
    return mapping_id

async def get_mapping_process_by_id(mapping_process_id: str, filter_dp: bool = None):
    mapping_process_docu = await mapping_repo.find_mapping_process_by_id(mapping_process_id)
    mapping = mapping_process_docu.mapping
    if(filter_dp is not None and filter_dp == True):
        # Filter mapping_process to retrieve only data properties components
        filered_by_dp = {k: v for k, v in mapping.items() if (getJsonSchemaPropertieType(k) != "" ) }
        mapping = filered_by_dp
    
    onto_id = mapping_process_docu.ontologyId
    ontology = await onto_service.get_ontology_by_id(onto_id)
    ontology_data = onto_service.build_ontology_response(ontology, onto_id)
    JSON_schema = await schema_service.get_schema_by_id(mapping_process_docu.jsonSchemaId)
    complete_mapping = build_mapping_proccess_response(ontology_data, JSON_schema, mapping, mapping_process_docu)

    return complete_mapping

async def get_mappings(validated_mappings: bool = None):
    query = {}
    if((validated_mappings is not None) and (validated_mappings == True)):
        query = {'mapping_suscc_validated': validated_mappings}
    print("query", query)
    mapping_process_docs_list = await mapping_repo.find_mappings_by_query(query)
    mappingpr_names = []
    for mapping_process_doc in mapping_process_docs_list:
        mappingpr = build_mapping_id_name_tupple(mapping_process_doc)
        mappingpr_names.append(mappingpr)

    return mappingpr_names

def build_mapping_id_name_tupple(mapping_process_doc):
    return  {
            "id": str(mapping_process_doc['_id']),
            "name": mapping_process_doc['name'],
    }

def build_mapping_proccess_response(ontology_data, JSON_schema, mapping, mapping_process_docu):
    return {
            'ontology': ontology_data,
            'schema': JSON_schema,
            'mapping': mapping,
            'mapping_name': mapping_process_docu.name
    }

async def update_whole_mapping_process(put_request: PutMappingRequest):
    if(put_request.mapping_proccess_id is None or put_request.mapping_proccess_id == ""):
        #json_schema_id = await schema_service.insert_schema(put_request.jsonSchema)
        full_collection_path = DLzone + put_request.documentStoragePath
        json_schema_id = await schema_service.get_or_create_schema(full_collection_path,put_request.jsonSchema)
        print("json_schema_id en update WHOLE", json_schema_id)
        mapping_process_docu = MappingProcessDocument(name=put_request.name, mapping=put_request.mapping,
                                                            ontologyId=put_request.ontology_id,
                                                            jsonSchemaId=str(json_schema_id),
                                                            document_storage_path = put_request.documentStoragePath,
                                                            mapping_suscc_validated=False)
        print("Previo al insert: ", mapping_process_docu)
        mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))
        return mapping_pr_id.inserted_id
    else:
        mapping_pr_id = await mapping_repo.find_mapping_process_by_id(put_request.mapping_proccess_id)
        if not mapping_pr_id:
            return "Mapping process not found"
        map_request = MappingRequest(name=put_request.name, mapping=put_request.mapping)
        mapping_updated = await update_mapping_process(map_request, put_request.mapping_proccess_id, False)
        return mapping_updated.acknowledged
    
async def get_evaluation_results_by_json(mapping_process_id: str, json_key: str, limit: int, offset:int):
    mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_process_id))
    schema_id = mapping_process.jsonSchemaId
    keys_list = find_json_keys(json_key)
    results = metadata_repo.get_evaluation_results(str(schema_id), keys_list, limit, offset)
    # if json_key not in json_schema_properties_keys:
    #     raise ValueError(f"Invalid JSON key: {json_key}")
    return results
 