

from app.repositories import mapping_repo, metadata_repo

from app.repositories.metadata_repo import ParamRepoCrateDQModel 
from app.dq_evaluation.evaluation import find_json_keys

from pydantic import BaseModel
from bson import ObjectId
from typing import Dict, Any

from app.models.mapping import FieldNode

async def get_evaluation_results_by_json(mapping_process_id: str, json_key: str, limit: int, offset:int):
    mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_process_id))
    schema_id = mapping_process.jsonSchemaId
    keys_list = find_json_keys(json_key)
    results = metadata_repo.get_evaluation_results(str(schema_id), keys_list, limit, offset)
    # if json_key not in json_schema_properties_keys:
    #     raise ValueError(f"Invalid JSON key: {json_key}")
    return results

class ParamCrateDQModel(BaseModel):
    mapping_process_id : str = None
    dq_model_name : str = None
    dq_method_id : str = None
    dq_aggregated_method_id : str = None

# TODO: ver si mandamos los nombres de los metodos agregados por aca, de momento va a estar hardcodeado
# create_dq_model(mapping_process_id: str,dq_model_name:str, mapped_entries: Dict[str, Any]):
async def create_dq_model(create_dq_params: ParamCrateDQModel, mapped_entries: Dict[str, Any]):
    print("### Create dq model in metadata service ###")
    mapping_process_docu = await mapping_repo.find_mapping_process_by_id(create_dq_params.mapping_process_id)
    # la ontología ya va a etsar creada y creo que el dataset tambien
    # creo que el contexto a esta altura ya esta creado
    print("### Got mapping proccess document ###", mapping_process_docu)
    save_dq_model_params = ParamRepoCrateDQModel(mapping_process_id=create_dq_params.mapping_process_id, dq_model_name=create_dq_params.dq_model_name, 
                                                dq_method_id=create_dq_params.dq_method_id, mapping_process_docu=mapping_process_docu, 
                                                dq_aggregated_method_id=create_dq_params.dq_aggregated_method_id, 
                                                mapped_entries=mapped_entries.keys())
    result = metadata_repo.save_data_quality_modedl(save_dq_model_params)
    return result

async def get_applied_methods_by_dq_model(dq_model_id: str):
    dq_methods = metadata_repo.get_applied_methods_by_dq_model(dq_model_id)
    # if json_key not in json_schema_properties_keys:
    #     raise ValueError(f"Invalid JSON key: {json_key}")
    return dq_methods

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

    result = metadata_repo.get_dq_models(onto_id, dataset_id, method_id, mapping_process_id)
    #2nd use metric id to filter the data quality models
    #Por cada uno de los DQModels obtener los AppliedDQMethod y estos van a tener que estar 
    #relacionados con el Method que se está aplicando a traves de HAS_METHOD


    # mapping_process_docu = await mapping_repo.find_mapping_process_by_id(mapping_process_id)
    # result = metadata_repo.get_data_quality_models(mapping_process_docu)
    print("result", result)
    return result

# TODO: posible pero no se si queda
async def get_method_by_metric():
    dq_methods = metadata_repo.get_applied_methods_by_dq_model()
    # if json_key not in json_schema_properties_keys:
    #     raise ValueError(f"Invalid JSON key: {json_key}")
    return dq_methods