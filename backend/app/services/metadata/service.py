from app.repositories.mapping.repository import MappingRepository
from app.repositories.metadata.repository import MetadataRepository
from app.rules_validation.mapping_rules import find_json_keys
from .types import CreateDQModelRequest, GetEvaluationResultsRequest
from app.repositories.metadata.types import SaveDQModelDTO

class MetadataService:
    def __init__(self, mapping_repository: MappingRepository, metadata_repository: MetadataRepository):
        self.mapping_repository = mapping_repository
        self.metadata_repository = metadata_repository

    async def get_evaluation_results_by_json(self, evaluation_params: GetEvaluationResultsRequest):
        """Get evaluation results for a specific JSON key."""
        mapping_process = await self.mapping_repository.find_by_id(evaluation_params.mapping_process_id)
        schema_id = mapping_process.jsonSchemaId
        keys_list = find_json_keys(evaluation_params.json_key)
        
        results, total_count = await self.metadata_repository.get_evaluation_results_v2(
            evaluation_params.dq_model_id,
            str(schema_id),
            keys_list,
            evaluation_params.limit,
            evaluation_params.offset
        )
        return results, total_count

    async def create_dq_model(self, create_params: CreateDQModelRequest, mapped_entries):
        """Create a new DQ model."""
        print("### Create dq model in metadata service ###" + create_params.dq_model_name)
        mapping_process_doc = await self.mapping_repository.find_by_id(create_params.mapping_process_id)
        print("### Got mapping proccess document ###", mapping_process_doc)
        
        save_dto = CreateDQModelRequest.to_save_dto(create_params, mapping_process_doc, mapped_entries)
        print("About to save DQ model:", save_dto)
        result = await self.metadata_repository.save_data_quality_model(save_dto)
        return result

    async def get_applied_methods_by_dq_model(self, dq_model_id: str):
        """Get applied methods for a DQ model."""
        return await self.metadata_repository.get_applied_methods_by_dq_model(dq_model_id)

    async def get_dq_models(self, mapping_process_id: str, method_id: str):
        """Get DQ models for a mapping process and method."""
        print("#Fetching DQModels#")
        print("mapping_process_id:", mapping_process_id)
        print("method_id:", method_id)

        map_process_info = await self.mapping_repository.find_by_id(mapping_process_id)
        onto_id = map_process_info.ontologyId
        dataset_id = map_process_info.jsonSchemaId

        result = await self.metadata_repository.get_dq_models(onto_id, dataset_id, method_id, mapping_process_id)
        print("result", result)
        return result

    async def get_data_quality_rules(self):
        """Get data quality rules."""
        data_quality_rules = await self.metadata_repository.get_data_quality_rules()
        print("data_quality_rules:", data_quality_rules)
        return data_quality_rules
