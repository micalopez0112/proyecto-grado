from ..database import  mapping_process_collection
from app.domain.mapping.models import EditMappingRequest
from bson import ObjectId

# find_mappings_by_schema gets all the mapping processes that use a specific JSON schema
async def find_mappings_by_schema(json_schema_id: str):
    cursor = mapping_process_collection.find({'jsonSchemaId': json_schema_id})
    mapping_process_docs = await cursor.to_list(length=None)
    
    return mapping_process_docs

# find_mapping_process_by_id gets a mapping process by its ID
async def find_mapping_process_by_id(mapping_pr_id: str):
    mapping_obj_id = ObjectId(mapping_pr_id)
    mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_obj_id})
    
    return mapping_process_docu

async def update_mapping_process(edit_mapping_request: EditMappingRequest, mapping_proccess_id: str, mapping_validated: bool):
    try:
        update_data = {'mapping_suscc_validated': mapping_validated}
        for key, value in edit_mapping_request:
            print("value", value)
            if value is not None and value != "" and value != {} and value != "string":
                update_data[key] = value

        query_to_update = {'_id': mapping_proccess_id}
        try_update =  {'$set': update_data}
        result = await mapping_process_collection.update_one(
            query_to_update,
            try_update
        )
    except Exception as e:
        print("Error in updating mapping process", e)
    
    return result