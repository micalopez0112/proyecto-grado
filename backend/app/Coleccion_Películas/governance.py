from neo4j import GraphDatabase
import os
import json
URI = "bolt://localhost:7687"
AUTH = ("neo4j","tesis2024")


print("AAAA")

def connect_to_governanceDB():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
            print("Connected to governanceDB")
            try:
                driver.verify_connectivity()
                generateMetadataFromJSON('C:/Users/fncastro/Documents/GitHub/APP/proyecto-grado/backend/app/Coleccion_Películas',
                                         driver);
                print("#Fin de la conexión#")
                driver.close()
            except Exception as e:
                  print("Error connecting to governanceDB: ", e)
                  

def generateMetadataFromJSON(CollectionPath : str, driver: GraphDatabase.driver):
      print("##Generating path from JSON##")
      ##generar nodo de la coleccion y asociarlo a la zona donde está almacenado
      
      collectionName = CollectionPath.split('/')[-1]
      collection_query = f""" 
        MERGE (zone:Zone {{ name: "trusted" }})
        CREATE (collection:Dataset:Collection {{
        name: "{collectionName}",
        description: "Colección que contiene información sobre varias películas",
        ingestion_date: "2024-10-11",
        ingestion_info: "(Referencia de donde se generó o llegó a la ingestion zone)",
        type: "json file"
        }})
        WITH collection, zone
        CREATE (collection)-[:STOREDIN]->(zone)
        RETURN elementId(collection) AS collectionElementId
      """
      collectionInsertResult = driver.execute_query(collection_query)
      collectionNode = collectionInsertResult[0]
      for item in collectionNode:
           collectionNodeId = item ['collectionElementId']
        ##Revisar si es al forma correcta de obtener la info del RETURN
      for collectionFileName in os.listdir(CollectionPath):
        if(collectionFileName.endswith(".json")):
            ###
            print("##Element id of Item: ", collectionNodeId)
            print("type of collectionNodeId: ", type(collectionNodeId))
            root_query = f"""
                MATCH (collection) WHERE elementId(collection) = '{collectionNodeId}'
                CREATE (doc:Documents {{
                id_document: "{collectionFileName}"
                }})
                CREATE (collection)<-[:BELONGSTOCOLLECTION]-(doc)
                RETURN elementId(doc) AS docElementId
                """ 
             ##Retornar el id del doc raíz para conectar los fields con el documento
            rootDocumentNode = driver.execute_query(root_query)
            documentNode = rootDocumentNode[0]
            for item in documentNode:
                documentNodeId = item ['docElementId']
            print(f"##Documento raíz: {rootDocumentNode}##")

    ########
             ##id_document no puede ser el nombre del archivo, debe ser un id único
            file_path = os.path.join(CollectionPath, collectionFileName)
            try:
                with open(file_path,'r') as collectionFile:
                    contentAsJson = json.load(collectionFile)
                    print(f"#Contenido del archivo: ${collectionFileName} #: ",contentAsJson)
                    for( key, value) in contentAsJson.items():
                        print(f"Key: {key} Value: {value}")
                        generateFieldsMetadata(driver,documentNodeId,key,value)  
            except json.JSONDecodeError as e:
                print(f"Error al decodificar el archivo {collectionFileName}: {e}")


def generateFieldsMetadata(driver:GraphDatabase.driver, parentDocId, field, field_value):
    print('##Generating fields metadata##')
    if isinstance(field_value, dict):
            # Es un documento embebido
            ## tenemos que crear un :Document y sus fields
            embedded_doc_var = f"doc_{field}"
            cypher_query = f"""
            MATCH (parentDoc) WHERE elementId(parentDoc) = '{parentDocId}'
            CREATE (field:Fields {{ name: "{field}", type: "Document" }})
            CREATE (field)-[:BELONGSTODOCUMENT]->(parentDoc)
            CREATE ({embedded_doc_var}:Documents {{ id_document: "{field}" }})
            CREATE (field)-[:BELONGSTODOCUMENT]->({embedded_doc_var})
            RETURN elementId({embedded_doc_var}) AS embeddedDocElementId
            """
            docResultQuery = driver.execute_query(cypher_query)
            documentNode = docResultQuery[0]
            for item in documentNode:
                documentNodeId = item ['embeddedDocElementId']
            # # entramos recursivo al documento embebido
            for sub_field_name, sub_field_value in field_value.items():
                # Llamar a la misma transacción para el documento embebido
                generateFieldsMetadata(driver, documentNodeId, sub_field_name, sub_field_value)
                print(f"aa for {documentNodeId}")
    elif isinstance(field_value, list):
            # Es un array
            # cypher_query = f"""
            # CREATE (field:Fields {{ name: "{field_name}", type: "Array" }})
            # CREATE (field)-[:BELONGSTODOCUMENT]->({parent_doc})
            # """
            print("completar para array")
            
    else:
            # Es un campo simple
            value_type = type(field_value).__name__.capitalize()
            cypher_query = f"""
            MATCH (parentDoc) WHERE elementId(parentDoc) = '{parentDocId}'
            CREATE (field:Fields {{ name: "{field}", type: "{value_type}", value: "{field_value}" }})
            CREATE (field)-[:BELONGSTODOCUMENT]->(parentDoc)
            """
            driver.execute_query(cypher_query)