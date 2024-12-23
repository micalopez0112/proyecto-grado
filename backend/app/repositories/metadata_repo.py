from typing import Dict, Any
from datetime import  datetime

from ..database  import neo4j_driver 
from app.models.mapping import DqResult



def execute_neo4j_query(query:str, params:Dict[str, Any]):
    with neo4j_driver.session() as session:
        result = session.run(query=query, parameters=params)
        return result.data()

def delete_existing_field_value_measures(json_keys, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f"""
        MATCH (c:Collection {{id_dataset: '{jsonSchemaId}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]

    delete_existing_measures = f"""
        {graph_path}
        MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
        DETACH DELETE m
    """
    neo4j_driver.execute_query(delete_existing_measures)


def insert_field_value_measures(json_keys, value, id_document, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f"""
        MATCH (c:Collection {{id_dataset: '{jsonSchemaId}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """

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
    
    neo4j_driver.execute_query(insert_measure)


def insert_field_measures(json_keys, value, jsonSchemaId):
    first_key = json_keys[0]
    graph_path = f""" 
        MATCH (c:Collection {{id_dataset: '{jsonSchemaId}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    latest_item = json_keys[-1]
    current_datetime = datetime.now()

    insert_measure = f"""
        CREATE (f{latest_item})-[:FieldMeasure]->(m:Measure {{measure: {value}, date: '{current_datetime}'}})
    """

    query = graph_path + insert_measure
    neo4j_driver.execute_query(query)

def insert_context_metadata(ontology_id, onto_name):
    query = f"""
        MERGE (ctx:Context {{name:'{onto_name}',id: '{ontology_id}'}})
    """
    neo4j_driver.execute_query(query)

def get_evaluation_results(json_schema_id, json_keys, limit, page_number):
    first_key = json_keys[0]
    graph_path = f""" 
        MATCH (c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """

    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    if page_number is None or page_number < 1:
        page_number = 1
    skip = (page_number - 1) * limit
    latest_item = json_keys[-1]

    select_measure = f"""
        {graph_path}-[fvm:FieldValueMeasure]->(measure) 
        RETURN f{latest_item}, measure, fvm
        SKIP {skip} 
        LIMIT {limit}
    """
    print("QUERY: ", select_measure)
    # returns record, summay, keys
    records, _, _ = neo4j_driver.execute_query(select_measure)
    results = []
    for record in records:
        dq = DqResult(name=record[0]['name'], id_document=record[2]['id_document'], 
                      date=record[1]['date'], 
                      measure=record[1]['measure'])
        results.append(dq)

    return results

def init_governance_zone():
    ## Hardcoded specific dimension, factor and metric for this project
    print("Going to init governance zone")
    ##Need to save 2 metrics one for each granularity level
    query = """
        MERGE (d:Dimension {id:'D1', name:'Accuracy'})
        WITH d
        MERGE (d)<-[:HAS_DIMENSION]-(f:Factor {id:'D1F1', name:'Syntactic Accuracy'})
        WITH f
        MERGE (f)<-[:HAS_FACTOR]-(m1:Metric {id:'D1F1M1', name:'Attribute Syntax', granularity:'Field Value',
             description:'The attribute value in the document collection is compared against its corresponding value in the domain ontology', method:'def compare_onto_with_json_value(onto_prop_value, json_value) :\n
                    if onto_prop_value == json_value:\n
                        return 1\n
                    else:\n
                        return 0 '})
        MERGE (f)<-[:HAS_FACTOR]-(m2:Metric {id:'D1F1M2', name:'Attribute Syntax', granularity:'Field',
          description:'',
          method:''})
    """
    with neo4j_driver.session() as session:
        result = session.run(query=query)
        return result.data()
    


