from neo4j import GraphDatabase
from datetime import date
from typing import Dict, Any
import os
import json
from neo4j import Session
from typing import Generator
from ..database  import neo4j_conn, neo4j_driver


ZONE = "trusted"
   
def generateMetadataV2(CollectionPath:str):
    try:
        print("## Create neo4j graph ##")
        ##Se obtiene el JSON Schema desde un file
        ##En el flujo se va a ejecutar generateMetadataFromSchema 
        ##al llamar el endpoint de generar el schema
        with open(CollectionPath,'r') as collectionFile:
            contentAsJson = json.load(collectionFile)
        json_properties = contentAsJson.get("properties")
        generateMetadataFromSchemaV2(CollectionPath,
                                    json_properties);
        print("#Fin de la conexión#")
    except Exception as e:
            print("Error connecting to governanceDB: ", e)

def generateMetadataFromSchemaV2(CollectionPath:str,schema: Dict[str, Any]):
    print("##Generating Collection metadata from it's Schema##")
    fecha = date.today()
    ##Asumimos que los metadatos están disponibles para ser creados en la Ingestion Zone => date = today
    collectionName = CollectionPath.split('/')[-1]
    collection_query = """
        MERGE (zone:Zone { name: $zoneName })
        CREATE (collection:Dataset:Collection {
            name: $collectionName,
            description: "Colección que contiene información sobre varias películas",
            ingestion_date: $ingestionDate,
            ingestion_info: $collectionPath,
            type: "json file"
        })
        WITH collection, zone
        CREATE (collection)-[:STOREDIN]->(zone)
        RETURN elementId(collection) AS collectionElementId
    """
    params = {
        'collectionName': collectionName,
        'ingestionDate': fecha,
        'collectionPath': CollectionPath,
        'zoneName': ZONE
    }
    #neo4j_driver = neo4j_conn.get_driver()
    with neo4j_driver.session() as session:
        collectionInsertResult = session.run(query=collection_query, parameters=params)
        print("connection successfully")
        collectionNode = collectionInsertResult.data()[0]

    collectionNodeId = collectionNode['collectionElementId']
    print(f'El elementId con el que se insertó la colección es: {collectionNodeId}')
    # for item in collectionNode:
    #     print("item:", item)
    #     print("JUSTO ANTES DE FALLAR")
    #     collectionNodeId = item['collectionElementId']
    #     print("fallo!")
    #     print(f'El elementId con el que se insertó la colección es: {collectionNodeId}')
    #     ##Revisar si es al forma correcta de obtener la info del RETURN
    
    ##Creamos los fields del schema
    for field_key, field_value in schema.items():
        try:
            generateFieldsMetadataV3(collectionNodeId,"schema",field_key,field_value)  
        except Exception as e:
            print(f"Error al crear el field {field_key}: {e}")
#    return collectionNodeId


##parentType = "schema" | "field" 
##Si no vamos a generar el schema se tendría que usar la relación belongs to Collection
def generateFieldsMetadataV3(parentNodeId:str, parentType:str, field:str, field_value: Dict[str, Any]):
    try:
        field_type = field_value.get("type")
        field_query = """
            MATCH (parent) WHERE elementId(parent) = $parentNodeId
            CREATE (field:Fields {
                id_field: "idfield",
                name: $fieldName,
                type: $fieldType
            })
            CREATE (field)-[:belongsTo]->(parent)
            SET field += { parentType: $parentType }
            RETURN elementId(field) AS fieldElementId
        """
        params = {
            'parentNodeId': parentNodeId,
            'fieldName': field,
            'fieldType': field_type,
            'parentType': parentType.capitalize()  # Capitalizamos aquí para la relación
        }
        #neo4j_driver = neo4j_conn.get_driver()
        with neo4j_driver.session() as session:
        # Ejecutar la consulta
            fieldInsertResult = session.run(query=field_query, parameters=params)
            fieldNode = fieldInsertResult.data()[0]           
            fieldNodeId = fieldNode['fieldElementId']
            print("## RESULT:",fieldNodeId)
            # for item in fieldNode:
            #     fieldNodeId = item ['fieldElementId']
        
        # Si el field es un objeto, recorrer sus propiedades de forma recursiva
        if field_type == "object":
            properties = field_value.get("properties", {})
            for sub_field_key, sub_field_value in properties.items():
                # Recursión: El campo padre ahora será el field que acabamos de crear
                generateFieldsMetadataV3(fieldNodeId,"field", sub_field_key, sub_field_value)
        elif field_type == "array":
            itemValue = field_value.get("items")
            generateFieldsMetadataV3(fieldNodeId,"field","items",itemValue )
    except Exception as e:
        print(f"Error al crear el NODO para field {field}: {e}")