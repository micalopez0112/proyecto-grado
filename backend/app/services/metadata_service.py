

from app.repositories import mapping_repo, metadata_repo
from app.services import schema_service, mapping_service
from app.dq_evaluation.evaluation import find_json_keys

from bson import ObjectId
from typing import Dict, Any

async def get_evaluation_results_by_json(mapping_process_id: str, json_key: str, limit: int, offset:int):
    mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_process_id))
    schema_id = mapping_process.jsonSchemaId
    keys_list = find_json_keys(json_key)
    results = metadata_repo.get_evaluation_results(str(schema_id), keys_list, limit, offset)
    # if json_key not in json_schema_properties_keys:
    #     raise ValueError(f"Invalid JSON key: {json_key}")
    return results


async def create_dq_model(mapping_process_id: str, mapped_entries: Dict[str, Any]):
    print("### Create dq model in metadata service ###")
    mapping_process_docu = await mapping_repo.find_mapping_process_by_id(mapping_process_id)
    # la ontología ya va a etsar creada y creo que el dataset tambien
    # creo que el contexto a esta altura ya esta creado
    print("### Got mapping proccess document ###", mapping_process_docu)
    result = metadata_repo.save_data_quality_modedl(mapping_process_docu, mapped_entries.keys())