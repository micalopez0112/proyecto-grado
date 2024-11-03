


from ..database import  jsonschemas_collection

async def find_all_schemas():
    cursor = jsonschemas_collection.find({})
    schemas_list = await cursor.to_list(length=None)
    
    return schemas_list