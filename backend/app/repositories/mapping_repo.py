from ..database import  mapping_process_collection

async def find_mappings_by_schema(json_schema_id: str):
    cursor = mapping_process_collection.find({'jsonSchemaId': json_schema_id})
    mapping_process_docs = await cursor.to_list(length=None)
    
    return mapping_process_docs