from typing import Dict, Any
from datetime import  datetime

from ..database  import neo4j_driver

def execute_neo4j_query(query:str, params:Dict[str, Any]):
    with neo4j_driver.session() as session:
        result = session.run(query=query, parameters=params)
        return result.data()

def execute_neo4j_query_by_driver(query:str):    
    neo4j_driver.execute_query(query)

# TODO : terminar
def delete_existing_field_value_measures(json_keys, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f"MATCH (c:Collection {{id_dataset: '{jsonSchemaId}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})"

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]

    delete_existing_measures = f"""
    {graph_path}
    MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
    DETACH DELETE m
    """
    
    print(f"delete_existing_measures: {delete_existing_measures}")
    
    neo4j_driver.execute_query(delete_existing_measures)


def insert_field_value_measures(json_keys, value, id_document, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f"MATCH (c:Collection {{id_dataset: '{jsonSchemaId}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})"

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]
    current_datetime = datetime.now()

    insert_measure = f"""
    {graph_path}
    MERGE (f{latest_item})-[:FieldValueMeasure {{id_document: {id_document}}}]->(m:Measure)
    SET m.measure = {value}, m.date = '{current_datetime}'
    """
    
    print(f"insert_measure: {insert_measure}")
    neo4j_driver.execute_query(insert_measure)


def insert_field_measures(json_keys, value, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f"MATCH (c:Collection {{id_dataset: '{jsonSchemaId}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})"

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]
    current_datetime = datetime.now()

    insert_measure = f"""
    CREATE (f{latest_item})-[:FieldMeasure]->(m:Measure {{measure: {value}, date: '{current_datetime}'}})
    """

    query = graph_path + insert_measure
    print(f"query: {query}")

    neo4j_driver.execute_query(query)
# TODO : terminar
# aca vendría: rootObject-contacto-city_key#string, limit, y offset/page
def get_evaluation_results(json_keys, jsonSchemaId, limit):
    first_key = json_keys[0]
    graph_path = f"MATCH (c:Collection {{id_dataset: {jsonSchemaId}}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})"

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]
    get_evaluation = f"""
     
    """
    # get_evaluation_results = f"""
    # {graph_path}
    # MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
    # RETURN m.measure as measure, m.date as date
    # """
    
    # print(f"get_evaluation_results: {get_evaluation_results}")
    
    # execute_neo4j_query_by_driver(get_evaluation_results)
