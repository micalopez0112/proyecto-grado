from neo4j import GraphDatabase
from datetime import date
from typing import Dict, Any
import os
import json
URI = "bolt://localhost:7687"
AUTH = ("neo4j","tesis2024")
ZONE = "trusted"

def generateMetadata(CollectionPath:str):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
            print("Connected to governanceDB")
            try:
                ##Se obtiene el JSON Schema desde un file
                ##En el flujo se va a ejecutar generateMetadataFromSchema 
                ##al llamar el endpoint de generar el schema
                with open(CollectionPath,'r') as collectionFile:
                    contentAsJson = json.load(collectionFile)
                driver.verify_connectivity()
                json_properties = contentAsJson.get("properties")
                generateMetadataFromSchema(CollectionPath,
                                         json_properties,
                                         driver);
                print("#Fin de la conexión#")
                driver.close()
            except Exception as e:
                  print("Error connecting to governanceDB: ", e)
                  

def generateMetadataFromSchema(CollectionPath:str,schema: Dict[str, Any], driver: GraphDatabase.driver):
    print("##Generating Collection metadata from it's Schema##")
    fecha = date.today()
    ##Asumimos que los metadatos están disponibles para ser creados en la Ingestion Zone => date = today
    collectionName = CollectionPath.split('/')[-1]
    collection_query = f""" 
        MERGE (zone:Zone {{ name: '{ZONE}' }})
        CREATE (collection:Dataset:Collection {{
        name: "{collectionName}",
        description: "Colección que contiene información sobre varias películas",
        ingestion_date: "{fecha}",
        ingestion_info: "{CollectionPath}",
        type: "json file"
        }})
        WITH collection, zone
        CREATE (collection)-[:STOREDIN]->(zone)
        RETURN elementId(collection) AS collectionElementId
      """
    collectionInsertResult = driver.execute_query(collection_query)
    collectionNode = collectionInsertResult[0]
    #type(collectionNode) <class 'list'>
    for item in collectionNode:
        collectionNodeId = item ['collectionElementId']
    print(f'El elementId con el que se insertó la colección es: {collectionNodeId}')
        ##Revisar si es al forma correcta de obtener la info del RETURN
    
    ##Creamos Schema Node, en nuestro caso es único entonces podemos crear directamente los fields
    # schema_query = f""" 
    #     MATCH (collection) WHERE elementId(collection) = '{collectionNodeId}'
    #     CREATE (schema: Schema )
    #     CREATE (collection)-[:hasSchema]->(schema)
    #     RETURN elementId(schema) AS schemaElementId
    # """
    # schemaInsertResult = driver.execute_query(schema_query)
    # schemaNode = schemaInsertResult[0]
    # for item in schemaNode:
    #     schemaNodeId = item ['schemaElementId']

    ##Creamos los fields del schema
    for field_key, field_value in schema.items():
        try:
            generateFieldsMetadataV2(driver,collectionNodeId,"schema",field_key,field_value)  
        except Exception as e:
            print(f"Error al crear el field {field_key}: {e}")
#    return collectionNodeId


##parentType = "schema" | "field" 
##Si no vamos a generar el schema se tendría que usar la relación belongs to Collection
def generateFieldsMetadataV2(driver:GraphDatabase.driver, parentNodeId:str, parentType:str, field:str, field_value: Dict[str, Any]):
    try:
        field_type = field_value.get("type")
        ##id_field = autogenerado? 
        field_query = f"""
            MATCH (parent) WHERE elementId(parent) = "{parentNodeId}"
            CREATE (field:Fields {{id_field:"idfield", name: "{field}", type: "{field_type}"}})
            CREATE (field)-[:belongsTo{parentType.capitalize()}]->(parent)
            RETURN elementId(field) AS fieldElementId
        """
        fieldInsertResult = driver.execute_query(field_query)
        fieldNode = fieldInsertResult[0]
        for item in fieldNode:
            fieldNodeId = item ['fieldElementId']
        
        # Si el field es un objeto, recorrer sus propiedades de forma recursiva
        if field_type == "object":
            properties = field_value.get("properties", {})
            for sub_field_key, sub_field_value in properties.items():
                # Recursión: El campo padre ahora será el field que acabamos de crear
                generateFieldsMetadataV2(driver,fieldNodeId,"field", sub_field_key, sub_field_value)
        elif field_type == "array":
            itemValue = field_value.get("items")
            generateFieldsMetadataV2(driver,fieldNodeId,"field","items",itemValue )
    except Exception as e:
        print(f"Error al crear el NODO para field {field}: {e}")