from ..database import  mapping_process_collection
from app.models.mapping import MappingProcessDocument
from bson import ObjectId

# find_mappings_by_schema gets all the mapping processes that use a specific JSON schema
async def find_mappings_by_schema(json_schema_id: str, validated_mappings: bool = None):
    query = {'jsonSchemaId': json_schema_id}
    if(validated_mappings is not None):
        query['mapping_suscc_validated'] = validated_mappings
        
    cursor = mapping_process_collection.find(query)
    mapping_process_docs = await cursor.to_list(length=None)
    
    return mapping_process_docs

# find_mapping_process_by_id gets a mapping process by its ID
async def find_mapping_process_by_id(mapping_pr_id: str):
    try:
        mapping_obj_id = ObjectId(mapping_pr_id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_obj_id})
        
        mapping_docu = MappingProcessDocument(**mapping_process_docu)
        print("Got mapping process document: ", mapping_docu)
        return mapping_docu
    except Exception as e:
        print("Error in updating mapping process", e)

# find_mappings_by_field finds a list of mappings that match a query
async def find_mappings_by_query(query):
    mapping_docus =  mapping_process_collection.find(query)
    mapping_docus_list = await mapping_docus.to_list(length=None)  
    return mapping_docus_list

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

async def delete_mapping_process_by_id(mapping_process_id: str) -> bool:
    mapping_object_id = ObjectId(mapping_process_id)
    result = await mapping_process_collection.delete_one({"_id": mapping_object_id})
    return result
  

