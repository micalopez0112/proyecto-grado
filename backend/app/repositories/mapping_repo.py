from ..database import  mapping_process_collection
from app.domain.mapping.models import EditMappingRequest, MappingProcessDocument
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

async def insert_mapping_process(mapping_process_docu: MappingProcessDocument):
    mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))

    return mapping_pr_id.inserted_id

async def update_mapping_process(data_to_update: dict, mapping_proccess_id: str, mapping_validated: bool):
    try:
        update_data = {'mapping_suscc_validated': mapping_validated}
        data_to_update.update(update_data)

        mapping_objectId = ObjectId(mapping_proccess_id)
        query_to_update = {'_id': mapping_objectId}
        try_update =  {'$set': data_to_update}

        result = await mapping_process_collection.update_one(
            query_to_update,
            try_update
        )
        return result
    except Exception as e:
        print("Error in updating mapping process", e)
    
    return None