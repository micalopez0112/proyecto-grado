from datetime import date
from typing import Dict, Any

from app.repositories.metadata_repo import execute_neo4j_query

import json

ZONE = "trusted"

    
def generate_metadata_from_schema(collection_path:str,schema: Dict[str, Any], id_dataset: str):
    today_date = date.today()
    ## Asumimos que los metadatos están disponibles para ser creados en la Ingestion Zone => date = today
    collection_name = schema.get("collection_name")
    collection_query = get_collection_query()
    params = {
        'collection_name': collection_name,
        'ingestion_date': today_date,
        'collection_path': collection_path,
        'zoneName': ZONE,
        'id_dataset' : id_dataset
    }
    collection_insert_result = execute_neo4j_query(collection_query, params)

    collection_node = collection_insert_result[0]
    collection_node_id = collection_node['collectionElementId']
    print(f'El elementId con el que se insertó la colección es: {collection_node_id}')
    schema_properties = schema.get("properties")
    ##Creamos los fields del schema
    for field_key, field_value in schema_properties.items():
        try:
            generate_fields_metadata(collection_node_id, "schema", field_key, field_value)  
        except Exception as e:
            print(f"Error al crear el field {field_key}: {e}")
#    return collectionNodeId


##parentType = "schema" | "field" 
## Si no vamos a generar el schema se tendría que usar la relación belongs to Collection
def generate_fields_metadata(parent_node_Id:str, parent_type:str, field:str, field_value: Dict[str, Any]):
    try:
        field_type = field_value.get("type")
        belongs_to = "belongsToField"
        if parent_type == "schema":
            belongs_to = "belongsToSchema"

        field_query = get_field_query(belongs_to)
        params = {
            'parentNodeId': parent_node_Id,
            'fieldName': field,
            'fieldType': field_type,
            'parentType': parent_type.capitalize(),  # Capitalizamos aquí para la relación
            'belongsTo': belongs_to
        }
      
        field_insert_result = execute_neo4j_query(field_query, params)
        field_node = field_insert_result[0]           
        field_node_id = field_node['fieldElementId']

        # Si el field es un objeto, recorrer sus propiedades de forma recursiva
        if field_type == "object":
            properties = field_value.get("properties", {})
            for sub_field_key, sub_field_value in properties.items():
                # Recursión: El campo padre ahora será el field que acabamos de crear
                generate_fields_metadata(field_node_id, "field", sub_field_key, sub_field_value)
        elif field_type == "array":
            itemValue = field_value.get("items")
            generate_fields_metadata(field_node_id, "field", "items",itemValue )
    
    except Exception as e:
        print(f"Error al crear el NODO para field {field}: {e}")

def get_field_query(belongs_to):
    return f"""
            MATCH (parent) WHERE elementId(parent) = $parentNodeId
            CREATE (field:Field {{
                id_field: "idfield",
                name: $fieldName,
                type: $fieldType
            }})
            CREATE (field)-[:{belongs_to}]->(parent)
            SET field += {{ parentType: $parentType }}
            RETURN elementId(field) AS fieldElementId
        """

def get_collection_query():
    return """
        MERGE (zone:Zone { name: $zoneName })
        CREATE (collection:Dataset:Collection {
            name: $collection_name,
            description: "Colección que contiene información sobre varias películas",
            ingestion_date: $ingestion_date,
            ingestion_info: $collection_path,
            type: "json file",
            id_dataset: $id_dataset
        })
        WITH collection, zone
        CREATE (collection)-[:STOREDIN]->(zone)
        RETURN elementId(collection) AS collectionElementId
    """