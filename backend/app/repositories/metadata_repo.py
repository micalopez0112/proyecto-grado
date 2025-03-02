from typing import Dict, Any, List
from datetime import  datetime
import uuid
import time

from ..database  import neo4j_conn
from app.models.mapping import DqResult, FieldNode,MappingProcessDocument
from app.dq_evaluation.evaluation import find_json_keys
from ..database import get_neo4j_driver

from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from unidecode import unidecode

import os

current_directory = Path(__file__).resolve().parent
methodONEKey = "D1F1M1MD1"
# TODO: ajustar estos nombres
method_name = "Method1"
method_name_columna = "Method2"

def execute_neo4j_query(query:str, params:Dict[str, Any]):
    neo4j_driver = get_neo4j_driver()
    with neo4j_driver.session() as session:
        result = session.run(query=query, parameters=params)
        return result.data()

def delete_existing_field_value_measures(data_model_id, json_keys, json_schema_id):
    first_key = json_keys[0]
    graph_path = f"""
        MATCH (dq:DQModel {{id: '{data_model_id.strip()}'}})
        -[:MODEL_DQ_FOR]->(c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
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

    print("DELETE QUERY: ", delete_existing_measures)
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.execute_query(delete_existing_measures)


def insert_field_value_measures(json_keys, value, id_document, json_schema_id):
    first_key = json_keys[0]
    graph_path = f"""
        MATCH (c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
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
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.execute_query(insert_measure)

# query to create the measure node with its value and corresponding related nodes: AppliedDqMethod and Field
def insert_field_value_measures_v2(field: FieldNode, value, id_document, dq_model_id, node_name):
    applied_dq_method_name = f"applied_dq_f{node_name}" 
    print("APPLIED DQ METHOD: ", applied_dq_method_name)
    current_datetime = datetime.now()
    # ver que esta pasando porque me crea doble los resultados de las medidas
    insert_measure_query = f"""
        MATCH (fieldNode) 
        WHERE elementId(fieldNode) = '{field.element_id}' 
        MATCH (fieldNode)<-[:APPLIED_TO]-(appliedMethod:AppliedDQMethod {{name: '{applied_dq_method_name}'}})<-[:HAS_APPLIED_DQ_METHOD]-(dq_model:DQModel {{id: '{dq_model_id}'}})
        CREATE (m:Measure)<-[:FieldValueMeasure {{id_document: {id_document}}}]-(fieldNode)
        CREATE (m)<-[:MODEL_MEASURE]-(appliedMethod)
        SET m.measure = {value}, m.date= '{current_datetime}'
    """
    print("## Evaluacion 4.6.1 - query:", insert_measure_query, " ##")
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.execute_query(insert_measure_query)

def insert_field_measures(field: FieldNode, node_name, value, dq_model_id):
    # TODO: sumar method id como parametro y buscar el appliedDqMethod que este asociado a ese method id
    # TODO: REVISAR porque creo que esta sumando doble
    print("LAST ITEM: ", node_name)
    current_datetime = datetime.now()

    applied_dq_method_name = f"applied_dq_f{node_name}col" # TODO: agregar _col / o cambiar a _aggregated 
    print("searching for: ",applied_dq_method_name )
    print("About to insert field measure for: ", field.element_id)
    query = f""" 
        MATCH (fieldNode) 
        WHERE elementId(fieldNode) = '{field.element_id}' 
        MATCH (fieldNode)<-[:APPLIED_TO]-(appliedMethod:AppliedDQMethod {{name: '{applied_dq_method_name}'}})
        <-[:HAS_APPLIED_DQ_METHOD]-(dq_model:DQModel {{id: '{dq_model_id}'}})
        CREATE (fieldNode)-[:FieldMeasure]->(m:Measure {{measure: {value}, date: '{current_datetime}'}})
        CREATE (m)<-[:MODEL_MEASURE]-(appliedMethod)
    """

    # for key in json_keys[1:]:
    #     node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
    #     graph_path += node_path

   

    print("About to make query: " + query)
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.execute_query(query)

# vieja implementacion
# def insert_field_measures(json_keys, value, json_schema_id):
#     # TODO: sumar method id como parametro y buscar el appliedDqMethod que este asociado a ese method id
#     first_key = json_keys[0]
#     graph_path = f""" 
#         MATCH (c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
#     """

#     for key in json_keys[1:]:
#         node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
#         graph_path += node_path

#     latest_item = json_keys[-1]
#     current_datetime = datetime.now()

#     insert_measure = f"""
#         CREATE (f{latest_item})-[:FieldMeasure]->(m:Measure {{measure: {value}, date: '{current_datetime}'}})
#     """

#     query = graph_path + insert_measure
#     neo4j_driver = get_neo4j_driver()
#     neo4j_driver.execute_query(query)

def insert_context_metadata(ontology_id, onto_name):
    query = f"""
        MERGE (ctx:Context {{name:'{onto_name}',id: '{ontology_id}'}})
    """
    with neo4j_conn.get_driver() as driver:
        driver.execute_query(query)

# TODO: borrar este metodo
def get_evaluation_results(json_schema_id, json_keys, limit, page_number):
    first_key = json_keys[0]
    graph_path = f""" 
        MATCH (c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """
    #MATCH (:Movie {title: 'Wall Street'})<-[:ACTED_IN]-(actor:Person)
    #RETURN actor.name AS actor
    #  MATCH (c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f:Field{{name: '{first_key}'}})
    
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
    neo4j_driver = get_neo4j_driver()
    records, _, _ = neo4j_driver.execute_query(select_measure)
    results = []
    for record in records:
        dq = DqResult(name=record[0]['name'], id_document=record[2]['id_document'], 
                      date=record[1]['date'], 
                      measure=record[1]['measure'])
        results.append(dq)

    return results

# TODO ver de sacar el id de la collecion y el 
def get_evaluation_results_v2(data_model_id, json_schema_id, json_keys, limit, page_number):
    first_key = json_keys[0]
    graph_path = f"""MATCH (dq:DQModel {{id: '{data_model_id.strip()}'}})
        -[:MODEL_DQ_FOR]->(c:Collection {{id_dataset: '{json_schema_id.strip()}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """
       
    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path

    if page_number is None or page_number < 1:
        page_number = 1
    skip = (page_number - 1) * limit
    latest_item = json_keys[-1]
    print("LATEST ITEM: ", latest_item)
    # TODO: ver porque no me sale
    select_measure = f"""
        {graph_path}-[fvm:FieldValueMeasure]->(measure)
        RETURN f{latest_item}, measure, fvm
        SKIP {skip} 
        LIMIT {limit}
    """
    print("QUERY: ", select_measure)
    # returns record, summay, keys
    neo4j_driver = get_neo4j_driver()
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
    save_quality_dimension()
    save_quality_factor()
    save_quality_metrics()
    save_quality_methods()
    print("Finished init governance zone")


def save_quality_dimension():
    # print("Se va a ejecutar save_quality_dimension")
    current_directory = Path(__file__).resolve().parent
    dimensions_file_path = current_directory / "dq_dimensions.csv"
    dimension_ds = pd.read_csv(dimensions_file_path);

    query_template = """
        MERGE ({dimension_var_name}:Dimension {{id:'{dimension_id}',name: '{dimension_name}'}})
    """
    
    query = ''
    for index, row in dimension_ds.iterrows():
        query += query_template.format(
            dimension_id = row['dimension_id'],
            dimension_name=row['name'],
            dimension_var_name=row['name'].lower(),
        )
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.execute_query(query)
    # with neo4j_driver.session() as session:
    #     result = session.run(query=query)
        
    # print("Se ejecutó save_quality_dimension")
    
def save_quality_factor():
    
    current_directory = Path(__file__).resolve().parent
    factor_file_path = current_directory / "dq_factors.csv"
    factor_ds = pd.read_csv(factor_file_path);
    
    query_template = """
        MERGE ({factor_var_name}:Factor {{name: '{factor_name}', id:'{factor_id}'}})
        MERGE ({factor_var_name})-[:HAS_DIMENSION]->(dim)
    """
    
    query = ''
    previous_dimension = ''
    for index, row in factor_ds.iterrows():
        
        if (row['dimension_id'] != previous_dimension):
            # no es la primera fila
            if (previous_dimension != ''):
                neo4j_driver = get_neo4j_driver()
                with neo4j_driver.session() as session:
                    result = session.run(query=query)
                    query = ''
            
            query += """
                MATCH (dim:Dimension {{id: '{dimension_id}'}})
                WITH dim
            """.format(dimension_id=row['dimension_id'])
        else:
            query += "WITH dim\n"

        factor_var_name = unidecode(row['name'].lower().replace(' ', "_").replace('-','_'))
        
        query += query_template.format(
            factor_name=row['name'],
            factor_var_name=factor_var_name,
            factor_id=row['factor_id'],
            dimension_id=row['dimension_id']
        )
        
        previous_dimension = row['dimension_id']
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.execute_query(query)
    # with neo4j_driver.session() as session:
    #     result = session.run(query=query)
        
def save_quality_metrics():
    neo4j_driver = get_neo4j_driver()
    metrics_file_path = current_directory / "dq_metrics.csv"
    metrics_ds = pd.read_csv(metrics_file_path);
    
    query_template = """        
        MERGE ({metric_var_name}: Metric {{id:'{metric_id}',name:'{metric_name}', granularity: '{metric_granularity}'}})
        MERGE ({metric_var_name})-[:HAS_FACTOR]->(factor)
    """

    query = ''
    previous_factor = ''
    for index, row in metrics_ds.iterrows():
        
        factor_var_name = unidecode(row['name'].lower().replace(' ', "_").replace('-','_'))

        if (row['factor_id'] != previous_factor):
            #no es la primera fila
            if (previous_factor != ''):
                neo4j_driver.execute_query(query)
                query = ''
            
            query += """
                MATCH (factor:Factor {{id: '{factor_id}'}})
                WITH factor
            """.format(factor_id=row['factor_id'])
        else:
            query += "WITH factor\n"

        metric_var_name = unidecode(row['name'].lower().replace(' ', "_").replace('-','_'))
        
        query += query_template.format(
            metric_name=row['name'],
            metric_var_name=metric_var_name,
            metric_granularity=row['granularity'],
            metric_id=row['metric_id'],
        )
        
        previous_factor = row['factor_id']
    neo4j_driver.execute_query(query)

def save_quality_methods():
    neo4j_driver = get_neo4j_driver()
    methods_file_path = current_directory / "dq_methods.csv"
    methods = pd.read_csv(methods_file_path);
    
    query_template = """        
        MERGE ({method_var_name}: Method {{id:'{method_id}',name:'{method_name}', description: '{method_description}', algorithm: '{method_algorithm}'}})
        MERGE ({method_var_name})-[:HAS_METRIC]->(metric)
    """

    query = ''
    previous_metric = ''
    for index, row in methods.iterrows():
        
        if (row['metric_id'] != previous_metric):
            #no es la primera fila
            if (previous_metric != ''):
                neo4j_driver.execute_query(query)
                query = ''
            
            query += """
                MATCH (metric:Metric {{id: '{metric_id}'}})
                WITH metric
            """.format(metric_id=row['metric_id'])
        else:
            query += "WITH metric\n"

        method_var_name = unidecode(row['name'].lower().replace(' ', "_").replace('-','_'))
        
        query += query_template.format(
            method_name=row['name'],
            method_description=row['description'],
            method_var_name=method_var_name,
            method_algorithm=row['algorithm'],
            method_id=row['method_id'],
        )
        
        previous_metric = row['metric_id']

    neo4j_driver.execute_query(query)

def get_last_node_in_nested_fields_query(json_schema_id: str, dq_model_id: str, json_keys):
    first_key = json_keys[0]
    graph_path = f""" 
        MATCH (collection)<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
    """
    last_node = "f"+ first_key
    ##initialize last_node with first_key in case no nested fields
    for key in json_keys[1:]:
        node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
        graph_path += node_path
        last_node = "f"+ key
        print("last key:",key)

    applied_dq_name = "applied_dq_" + last_node
    applied_dq_name_col = "applied_dq_" + last_node + "col" # ver de cambiar nombre, col queda mas entendible
    # TODO: ver si la relacion entre applied method y method queda hacia este lado o hacia el otro
    # quizas aca todo el app_dq_method: ... lo puedo cambiar por app_dq_method
    # (app_dq_method:AppliedDQMethod  {{name: '{applied_dq_name}'}}
    create_dq_method_q = f""" 
        WITH collection, {last_node}, dq_model, dq_method, dq_method_col
        MERGE ({last_node})<-[:APPLIED_TO]-(app_dq_method:AppliedDQMethod 
        {{name: '{applied_dq_name}'}})
        MERGE ({last_node})<-[:APPLIED_TO]-(app_dq_method_col:AppliedDQMethod 
        {{name: '{applied_dq_name_col}'}})
        MERGE (dq_method)<-[:APPLIES_METHOD]-(app_dq_method)
        MERGE (dq_method_col)<-[:APPLIES_METHOD]-(app_dq_method_col)
        MERGE (dq_model)-[:HAS_APPLIED_DQ_METHOD]->(app_dq_method_col)
        MERGE (dq_model)-[:HAS_APPLIED_DQ_METHOD]->(app_dq_method)
    """

    graph_path += create_dq_method_q
    print("builded query: ", graph_path)
    return graph_path

class ParamRepoCrateDQModel(BaseModel):
    mapping_process_id : str = None
    dq_model_name : str = None
    dq_method_id : str = None
    mapping_process_docu: MappingProcessDocument # ver si funciona
    dq_aggregated_method_id : str = None
    mapped_entries: List[str]
    
# TODO: retorna true si existe un dq model con el mismo contexto, dataset y que tenga appliedDqMethod para todos los atributos mapeados

# La query inicial trae el/los dq_model que tengan el contexto y el dataset 
# se recorre cada uno y :
## Usar la función get_applied_methods_by_dq_model retorna el nombre de todos los fields unidos por '-'
## Por cada dq_model:
    ## Recorrer los json_keys, 
        ## si están en el resultado de la función get_applied_methods_by_dq_model se saca
        ## sino break al siguiente DQ_MODEL
    ## si llega al final para un dq_model y ambas listas son vacías return ese dq_model
    ## sino seguir con el siguiente dq_model
# si no se encontró ningun dq_model se retorna None
def get_dq_model(ontology_id, json_schema_id, attributes_mapped):
    looked_fields = []
    for attribute in attributes_mapped:
        attr_keys = attribute.split('_')[0]
        attr_keys = '-'.join(attr_keys.split('-')[1:])
        looked_fields.append(attr_keys)
        print("attr_keys: ", attr_keys)
    query = f"""
         MATCH (ctx:Context {{id: '{ontology_id}'}})<-[:MODEL_CONTEXT]-(dq_model:DQModel)-[:MODEL_DQ_FOR]->(ds:Collection {{id_dataset: '{json_schema_id}'}})
         RETURN dq_model.id, dq_model.name
     """
    print("#query for checking if dq model exist#: ", query)
    print("Locked Fields: ", looked_fields)
    neo4j_driver = get_neo4j_driver()
    try:
        records, _, _ = neo4j_driver.execute_query(query)
        if(records.__len__() > 0):
            for record in records:## recorrer cada dq_model
                dq_model_id = record.get('dq_model.id')
                list_of_fields = get_applied_methods_by_dq_model(dq_model_id)
                # print("#dqmodel ID#: ", dq_model_id)
                print("#list_of_fields de dq_model#: ", list_of_fields)
                counter = 0
                for field in list_of_fields:
                    # print("##dq_model_applied_field: ", field)
                    if(field.name in looked_fields):
                        counter += 1
                print("Counter al finalizar el recorrido de list_of_fields: ", counter)
                if counter == len (list_of_fields):
                    return {
                        "id": dq_model_id,
                        "name": record.get('dq_model.name')
                    }
            return None
        else:
            return None
    except Exception as e:
        print("error in executing query: ", e)
        return None
    


# TODO: ver de cambiar el nombre de Collection a Dataset quizas
# CREATE (charlie:Person:Actor {name: 'Charlie Sheen'})-[:ACTED_IN {role: 'Bud Fox'}]->(wallStreet:Movie 
# {title: 'Wall Street'})<-[:DIRECTED]-(oliver:Person:Director {name: 'Oliver Stone'})
# save_data_quality_modedl(mapping_process_id, dq_model_name, mapping_process_docu, mapped_entries: List[str]):
def save_data_quality_modedl(save_dq_params: ParamRepoCrateDQModel):
    print("### Starting save data quality model process in neo4j ###")
    print("### Model dq entries : ###", save_dq_params.mapped_entries)
    mapping_process_docu = save_dq_params.mapping_process_docu
    ontology_id = mapping_process_docu.ontologyId
    json_schema_id = mapping_process_docu.jsonSchemaId
    dq_model_id = str(uuid.uuid4()) # ver que hacemos con esto
    timestamp_milliseconds = int(time.time() * 1000)
    print("##First check if dq model with same context, dataset and appliedDqMethod's exists")
    dq_model_already_exists = get_dq_model(ontology_id, json_schema_id, save_dq_params.mapped_entries)
    if (dq_model_already_exists):
        print("DQ Model already exists, with the info: ", dq_model_already_exists)
        print("#########")
        return dq_model_already_exists
    # dq_model_name = "dq_model_" + str(timestamp_milliseconds)
    # Aca empieza la query de construccion, se matchean todos los nodos principales
    # dq_method, contexto, collection, dq_model (el que se va a crear)
    # tenemos dos dq_method, el de granularidad celda y el de granularidad columna
    # TODO cambiar dq_method por ID y no por nombre
    # TODO: ver de donde sacamos "correctamnete" el method_name :(, aca esta harcodeado
    # ver si cambiamos el method_name por el id?
    print(" ## METHOD ID: ", save_dq_params.dq_method_id)
    print(" ## METHOD ID AGG: ", save_dq_params.dq_aggregated_method_id)
    # TODO validar datos
    query = f""" 
        MATCH (dq_method:Method {{id: '{save_dq_params.dq_method_id}'}})
        MATCH (dq_method_col:Method {{id: '{save_dq_params.dq_aggregated_method_id}'}})
        MERGE (context:Context {{name: 'context', id: '{ontology_id}'}})
        MERGE (collection:Collection {{id_dataset: '{json_schema_id}'}})
        MERGE (dq_model:DQModel  {{name: '{save_dq_params.dq_model_name}', id: '{dq_model_id}', mapping_process_id: '{save_dq_params.mapping_process_id}'}})
        MERGE (dq_model)-[:MODEL_CONTEXT]->(context)
        MERGE (dq_model)-[:MODEL_DQ_FOR]->(collection)
    """
    
    # en mapped_entries tengo:
    #{rootObject-imdbId_key#string: [{name: "sameAs", iri: "http://schema.org/sameAs"}]}
    attributes_mapped = save_dq_params.mapped_entries
    for attribute in attributes_mapped:
        print("attribute mapped: ", attribute)
        json_keys = find_json_keys(attribute)
        print("json keys: ", json_keys)
        query += " WITH collection, dq_model, dq_method, dq_method_col"
        add_applied_method_query = get_last_node_in_nested_fields_query(json_schema_id,dq_model_id, json_keys)
        print("add_applied_method_query: ", add_applied_method_query)
        query += add_applied_method_query
        # ['rootObject', 'imdbId']    
   
    print("### Query for creating dq model ###", query)
    try:
        neo4j_driver = get_neo4j_driver()
        neo4j_driver.execute_query(query)
        return dq_model_id
    except Exception as e:
        print("error in executing query: ", e)
        return None
    # necesito recorrer las mapped entries y crear un applied dq method y
    
def get_dq_models(onto_id, dataset_id, method_id, mapping_process_id):
    query = f"""
        MATCH (ctx:Context {{id: '{onto_id}'}})<-[:MODEL_CONTEXT]-(dq_model:DQModel)-[:MODEL_DQ_FOR]->(ds:Collection {{id_dataset: '{dataset_id}'}})
        WITH dq_model
        MATCH (dq_model {{mapping_process_id: '{mapping_process_id}'}})-[:HAS_APPLIED_DQ_METHOD]->(app_dq_method:AppliedDQMethod)-[:APPLIES_METHOD]->(method:Method {{id: '{method_id}'}})
        RETURN dq_model.id, dq_model.name
    """
    # WITH dq_model, app_dq_method, method
    # MATCH (att:Field)-[:APPLIED_TO]->(app_dq_method)
    neo4j_driver = get_neo4j_driver()
    try:
        records, _, _ = neo4j_driver.execute_query(query)
        return_info = {}
        if(records.__len__() > 0):
            for record in records:
                dq_model_id = record.get('dq_model.id')
                dq_model_name = record.get('dq_model.name')
                if (dq_model_id and dq_model_name):
                    # if dq_model_id not in return_info:
                    #     return_info[dq_model_id] = []
                    return_info[dq_model_id] = dq_model_name
                else:
                    print("No dq model id or attribute name")
        else:
            print("No data found")
        print("Return info: ", return_info)
        return return_info
    except Exception as e:
        print("error in executing query: ", e)
        return None

# get_applied_methods_by_dq_model returns the nodes that say in witch fields the method will be applied (kinda)
def get_applied_methods_by_dq_model(dq_model_id) -> List[FieldNode]:
    methodName = "Method1"
    # TODO: revisar porqque hice una moidificacion rara
    # query = f"""
    #     MATCH path = (dq_model:DQModel {{id: '{dq_model_id}'}})
    #     -[:HAS_APPLIED_DQ_METHOD]->(applied:AppliedDQMethod)
    #     -[:APPLIED_TO]->(startNode:Field)-[:belongsToField*0..]->(endNode) 
    #      WHERE EXISTS {{
    #      MATCH (applied)-[:APPLIES_METHOD]->(method:Method {{name: '{methodName}'}})}}
    #     RETURN nodes(path)[1..] AS nodes, relationships(path) AS relationships
        
    # """## VER SI ESTA ES LA FORMA CORRECTA DE OBTENER LOS FIELDS
       ##LO VAMOS A TENER QUE EXPLICAR EN EL INFORME
    #    ORDER BY size([rel IN relationships(path) WHERE type(rel) = 'belongsToField']) DESC
    #    LIMIT 1
    print("About to return Fields")
    query = f"""
    MATCH path = (dq_model:DQModel {{id: '{dq_model_id}'}})
    -[:HAS_APPLIED_DQ_METHOD]->(applied:AppliedDQMethod)
    -[:APPLIED_TO]->(startNode:Field)
    -[:belongsToField*0..]->(endNode)-[:belongsToSchema]->(col:Collection) 
    WHERE EXISTS {{
        MATCH (applied)-[:APPLIES_METHOD]->(method:Method {{name: '{methodName}'}})}}
    WITH endNode, path, size([rel IN relationships(path) WHERE type(rel) = 'belongsToField']) AS depth
    ORDER BY depth DESC
    WITH endNode, collect(path)[0] AS longest_path
    RETURN nodes(longest_path)[1..] AS nodes, relationships(longest_path) AS relationships
    """
    print(f"## {query}")
    try:
        neo4j_driver = get_neo4j_driver()
        records, _, _ = neo4j_driver.execute_query(query)
        results = []
        # print("RECORDS: ", records)
        # OJO: meti ese cambio ver si no da problema
        # records = records[1:]
        # print("RECORDS LEN: ", records.__len__())
        print("##########")
        for record in records:
            nodes = record[0]
            print("NODES: ", nodes)
            attribute_path_list = []
            # esto recorre todo el camino de nodos anidados para armar el string de atributos
            # donde se encuantra anidado
            for node in nodes[1:len(nodes)-1]: # se skipea el primero porque es el applied_dq
                print("NODE: ", node)
                attribute_path_list.insert(0, node['name'])
                print("ATTRIBUTE PATH: ", attribute_path_list)
            attribute_path = "-".join(attribute_path_list)
            fieldNode = FieldNode(element_id=nodes[1].element_id, name=attribute_path, type=nodes[1]['type'])
            results.append(fieldNode)    
        print("RESULTS: ", results)
        return results
    except Exception as e:
        print("error in executing query: ", e)
        return e



def get_node_by_element_id(element_id: str):
    match_query = f"""
        MATCH (n) 
        WHERE elementId(n) = '{element_id}' 
        RETURN n
    """
    neo4j_driver = get_neo4j_driver()
    records, _, _ = neo4j_driver.execute_query(match_query)
    print("RESULT: ",records)
    return records

def get_mapping_id_by_dq_model(dq_model_id: str):
    match_query = f"""
        MATCH (dq:DQModel  {{id: '{dq_model_id}'}}) 
        return dq.mapping_process_id as mapping_process_id
    """
    neo4j_driver = get_neo4j_driver()
    result, _, _ = neo4j_driver.execute_query(match_query)
    print("RESULT: ",result[0]['mapping_process_id'])
    return result[0]['mapping_process_id']

from collections import defaultdict

def get_data_quality_rules():
    match_query = """
        MATCH (d:Dimension)<-[:HAS_DIMENSION]-(f:Factor)<-[:HAS_FACTOR]-(m:Metric)<-[:HAS_METRIC]-(me:Method)
        RETURN d.name AS dimension, f.name AS factor, m.granularity AS granularity, me.id AS method_id
    """
    neo4j_driver = get_neo4j_driver()
    result, _, _ = neo4j_driver.execute_query(match_query)

    # Step 1: Organize results by dimension and factor
    data_structure = defaultdict(lambda: defaultdict(list))

    for record in result:
        dimension = record["dimension"]
        factor = record["factor"]
        granularity = record["granularity"]
        method_id = record["method_id"]

        # Store methods under their respective factor
        data_structure[dimension][factor].append({"granularity": granularity, "method_id": method_id})

    # Step 2: Transform into required format
    final_data = []

    for dimension, factors in data_structure.items():
        dimension_obj = {"dimension": dimension, "factors": []}

        for factor, methods in factors.items():
            # Separate value and field granularities
            value_methods = [m for m in methods if m["granularity"] == "value"]
            field_methods = [m for m in methods if m["granularity"] == "field"]

            # Pair them together
            metrics = []
            for v, f in zip(value_methods, field_methods):
                metrics.append({
                    "method_id": v["method_id"],
                    "agg_method_id": f["method_id"],
                    "name": f"Metric {len(metrics) + 1}"  # Assign metric names dynamically
                })

            dimension_obj["factors"].append({"name": factor, "metrics": metrics})

        final_data.append(dimension_obj)

    return final_data
