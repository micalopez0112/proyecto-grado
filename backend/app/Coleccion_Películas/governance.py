from neo4j import GraphDatabase
from datetime import date
from typing import Dict, Any
import os
import json
URI = "bolt://localhost:7687"
AUTH = ("neo4j","proyecto-grado123")
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
                print("aca paso 1")
                json_properties = contentAsJson.get("properties")
                print("aca paso 2")
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
## TODO:
## VER: que ids le ponemos al dq_model o que nombres para encontrarlos
##
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
        return None