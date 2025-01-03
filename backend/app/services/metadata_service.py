

from app.repositories import mapping_repo, metadata_repo
from app.services import schema_service, mapping_service
from app.dq_evaluation.evaluation import find_json_keys

from bson import ObjectId
from typing import Dict, Any

from app.models.schema import JsonSchema

async def get_evaluation_results_by_json(mapping_process_id: str, json_key: str, limit: int, offset:int):
    mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_process_id))
    schema_id = mapping_process.jsonSchemaId
    keys_list = find_json_keys(json_key)
    results = metadata_repo.get_evaluation_results(str(schema_id), keys_list, limit, offset)
    # if json_key not in json_schema_properties_keys:
    #     raise ValueError(f"Invalid JSON key: {json_key}")
    return results


async def create_dq_model(mapping_process_id: str, mapped_entries: Dict[str, Any]):
    mapping_process_docu = await mapping_repo.find_mapping_process_by_id(mapping_process_id)

    # la ontología ya va a etsar creada y creo que el dataset tambien
    # creo que el contexto a esta altura ya esta creado
    result = metadata_repo.save_data_quality_modedl(mapping_process_docu, mapped_entries)


async def get_dq_models(mapping_process_id: str, method_id: str):
    #1st obtain from context and dataset the data quality models
    #con el id del mapping obtener el id de la ontologia(contexto) y el dataset
    #con esos ids generar query en neo4j para obtener todos los DQModels
    #el contexto se relaciona a través de modelContext(MODEL_CONTEXT) 
    #y el dataset a traves de ModelsDQFor (MODEL_DQ_FOR)
    print("#Fetching DQModels#")
    print("mapping_process_id: ", mapping_process_id)
    print("method_id: ", method_id)

    map_process_info = await mapping_repo.find_mapping_process_by_id(mapping_process_id)
    
    onto_id = map_process_info.ontologyId
    dataset_id = map_process_info.jsonSchemaId

    print("#IDs#")
    print("Context id: ", onto_id)
    print("Dataset id: ", dataset_id)

    result = metadata_repo.get_dq_models(onto_id, dataset_id, method_id)
    #2nd use metric id to filter the data quality models
    #Por cada uno de los DQModels obtener los AppliedDQMethod y estos van a tener que estar 
    #relacionados con el Method que se está aplicando a traves de HAS_METHOD


    # mapping_process_docu = await mapping_repo.find_mapping_process_by_id(mapping_process_id)
    # result = metadata_repo.get_data_quality_models(mapping_process_docu)
    
    return result