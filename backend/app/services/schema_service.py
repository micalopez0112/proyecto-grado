

from typing import Dict, Any
from app.repositories import schema_repo
from app.models.schema import JSONSchemaResponse
from app.repositories.build_movies_metadata import generate_metadata_from_schema
from ..database import DLzone
from app.models.schema import JsonRequestList

from genson import SchemaBuilder

import json



async def get_all_schemas():
    schemas = await schema_repo.find_all_schemas()
    result = []
    for schema in schemas:
        # TODO ajustar nombre de la colección
        collection_name = schema.get('collection_name')
        if collection_name is None:
            collection_name = "some_collection"
        jsonSchema = JSONSchemaResponse(id=str(schema['_id']), collection_name=collection_name, properties=schema['properties'])
        result.append(jsonSchema)
        
    # TODO ajustar tipo de retorno
    return result

async def get_schema_by_id(schema_id: str):
    schema = await schema_repo.find_schema_by_id(schema_id)
    return schema

async def insert_schema(json_schema: dict):
    schema_id = await schema_repo.insert_schema(json_schema)
    return schema_id

async def find_schema_by_collection_name(collection_name : str):
    schema = await schema_repo.find_one_schema_by_query({'collection_name': collection_name})
    return schema

async def get_or_create_schema(collectionPath:str,json_schema: Dict[str, Any]):
    collection_name=json_schema['collection_name']
    existent_schema = await find_schema_by_collection_name(collection_name)
    if existent_schema is None:
        inserted_id = await insert_schema(json_schema)
        ## generate schema metadata
        print("INSERTED ID #####:", inserted_id)
        generate_metadata_from_schema(collectionPath, json_schema, str(inserted_id))
        return inserted_id
    
    return existent_schema.id

def generate_schema_from_collection (collectionFilePath: str):
    try:
        
        realPath = DLzone + collectionFilePath
        with open (realPath ,"r" ,encoding='utf-8') as file:
            builder = SchemaBuilder()
            # data = await file.read()
            file_content = json.load(file)
            json_data = JsonRequestList(jsonInstances=file_content)
            for json_obj in json_data.jsonInstances:
                builder.add_object(json_obj)
            schema = builder.to_schema()
            ##add method to clean nulls
            modified_schema = cleanJsonSchema(schema)
            return modified_schema
    except OSError as fileError:
        print("Error en la lectura del archivo de la colección", fileError)
        raise Exception("Error en la lectura del archivo de la colección")

def cleanJsonSchema (jsonSchema:Dict[str,Any])->Dict[str,Any]:
    try:
        properties = jsonSchema.get("properties", {})
        for field_key, field_value in properties.items():
            entry_type = field_value.get("type")

            if isinstance (entry_type,list):
                entry_type = [x for x in entry_type if x != "null"]
                if(entry_type):
                    field_value["type"] = entry_type[0]
                else:
                    print(f"No se encontró un tipo valido para el campo {field_key}")
            
           
            elif entry_type is None and field_value.get("anyOf") != None:
                anyOf = field_value.get("anyOf")
                print(f"El campo {field_key} tiene anyOf y es: {anyOf}")
                entry_type = [item for item in anyOf if item.get("type") != "null"]
                if entry_type:
                    print(f"El type que se debe agregar es: {entry_type[0]}")
                    properties[field_key] = entry_type[0]
                    #field_value = entry_type[0]
                    print(f"El field_value es: {field_value}")
                    # Llamar a cleanJsonSchema si el tipo resultante es un objeto o array
                    if entry_type[0].get("type") == "object":
                        cleanJsonSchema(entry_type[0])

                    elif entry_type[0].get("type") == "array":
                        items_value = entry_type[0].get("items", {})
                        if isinstance(items_value, dict):
                            cleanJsonSchema(items_value)

            ##Tenemos que limpiar dentro del entry_type si es un objeto o un array
            
            if field_value.get("type") == "object":
                cleanJsonSchema(field_value)

            elif field_value.get("type") == "array":
                items_value = field_value.get("items", {})
                if isinstance(items_value, dict):
                    cleanJsonSchema(items_value)

        return jsonSchema
    except Exception as e:
        print(f"Error al limpiar el schema: {e}")
        return None