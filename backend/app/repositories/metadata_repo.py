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
def insert_or_update_field_value_measure_2(json_keys, value, id_document, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f"MATCH (c:Collection {{id_dataset: {jsonSchemaId}}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})"

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]
    current_datetime = datetime.now()

    insert_measure = f"""
    MERGE (f{latest_item})-[:FieldValueMeasure {{id_document: {id_document}}}]->(m:Measure)
    SET m.measure = {value}, m.date = '{current_datetime}'
    """

    query = graph_path + insert_measure
    print(f"query value: {query}")

    execute_neo4j_query_by_driver(query)