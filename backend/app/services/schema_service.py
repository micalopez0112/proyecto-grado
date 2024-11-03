


from app.repositories import schema_repo
from app.domain.mapping.models import JSONSchemaResponse

async def get_all_schemas():
    schemas = await schema_repo.find_all_schemas()
    result = []
    for schema in schemas:
        # TODO ajustar nombre de la colección
        jsonSchema = JSONSchemaResponse(id=str(schema['_id']), collection_name="some_name")
        result.append(jsonSchema)
        
    # TODO ajustar tipo de retorno
    return result