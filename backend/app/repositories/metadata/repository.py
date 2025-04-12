from typing import Dict, Any, List
from datetime import datetime
import uuid
import time
from bson import ObjectId
from pathlib import Path

from app.database import get_neo4j_driver
from app.models.mapping import DqResult, FieldNode, MappingProcessDocument
from app.rules_validation.mapping_rules import find_json_keys
from app.repositories.metadata.types import SaveDQModelDTO

class MetadataRepository:
    def __init__(self, neo4j_driver=None):
        self.neo4j_driver = neo4j_driver or get_neo4j_driver()

    def execute_neo4j_query(self, query: str, params: Dict[str, Any] = None):
        """Execute a Neo4j query with optional parameters."""
        with self.neo4j_driver.session() as session:
            result = session.run(query=query, parameters=params or {})
            return result.data()

    async def delete_field_value_measures(self, data_model_id, json_keys, json_schema_id):
        first_key = json_keys[0]
        graph_path = f"""
            MATCH (dq:DQModel {{id: '{data_model_id.strip()}'}})
            -[:MODEL_DQ_FOR]->(c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
        """

        for key in json_keys[1:]:
            node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
            graph_path += node_path

        latest_item = json_keys[-1]
        delete_query = f"""
            {graph_path}
            MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
            DETACH DELETE m
        """
        
        self.neo4j_driver.execute_query(delete_query)

    async def insert_field_value_measures(self, field: FieldNode, value, id_document, dq_model_id, node_name):
        applied_dq_method_name = f"applied_dq_f{node_name}"
        current_datetime = datetime.now()
        
        insert_measure_query = f"""
            MATCH (fieldNode) 
            WHERE elementId(fieldNode) = '{field.element_id}' 
            MATCH (fieldNode)<-[:APPLIED_TO]-(appliedMethod:AppliedDQMethod {{name: '{applied_dq_method_name}'}})<-[:HAS_APPLIED_DQ_METHOD]-(dq_model:DQModel {{id: '{dq_model_id}'}})
            CREATE (m:Measure)<-[:FieldValueMeasure {{id_document: {id_document}}}]-(fieldNode)
            CREATE (m)<-[:MODEL_MEASURE]-(appliedMethod)
            SET m.measure = {value}, m.date= '{current_datetime}'
        """
        
        self.neo4j_driver.execute_query(insert_measure_query)

    async def insert_field_measures(self, field: FieldNode, node_name, value, dq_model_id):
        current_datetime = datetime.now()
        applied_dq_method_name = f"applied_dq_f{node_name}col"

        query = f"""
            MATCH (fieldNode) 
            WHERE elementId(fieldNode) = '{field.element_id}' 
            MATCH (fieldNode)<-[:APPLIED_TO]-(appliedMethod:AppliedDQMethod {{name: '{applied_dq_method_name}'}})<-[:HAS_APPLIED_DQ_METHOD]-(dq_model:DQModel {{id: '{dq_model_id}'}})
            CREATE (m:Measure)<-[:FieldMeasure]-(fieldNode)
            CREATE (m)<-[:MODEL_MEASURE]-(appliedMethod)
            SET m.measure = {value}, m.date= '{current_datetime}'
        """
        
        self.neo4j_driver.execute_query(query)

    async def get_evaluation_results_v2(self, data_model_id, json_schema_id, json_keys, limit, offset):
        first_key = json_keys[0]
        graph_path = f"""
            MATCH (dq:DQModel {{id: '{data_model_id.strip()}'}})
            -[:MODEL_DQ_FOR]->(c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
        """

        for key in json_keys[1:]:
            node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
            graph_path += node_path

        latest_item = json_keys[-1]
        query = f"""
            {graph_path}
            MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
            WITH m, r
            ORDER BY r.id_document
            SKIP {offset}
            LIMIT {limit}
            RETURN m.measure as measure, m.date as date, r.id_document as id_document
        """

        count_query = f"""
            {graph_path}
            MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
            RETURN count(m) as total
        """

        results = self.execute_neo4j_query(query)
        count_result = self.execute_neo4j_query(count_query)
        total_count = count_result[0]["total"] if count_result else 0

        return results, total_count

    async def get_dq_models(self, onto_id, dataset_id, method_id, mapping_process_id):
        query = f"""
            MATCH (ctx:Context {{id: '{onto_id}'}})<-[:MODEL_CONTEXT]-(dq_model:DQModel)-[:MODEL_DQ_FOR]->(ds:Collection {{id_dataset: '{dataset_id}'}})
            WITH dq_model
            MATCH (dq_model {{mapping_process_id: '{mapping_process_id}'}})-[:HAS_APPLIED_DQ_METHOD]->(app_dq_method:AppliedDQMethod)-[:APPLIES_METHOD]->(method:Method {{id: '{method_id}'}})
            RETURN dq_model.id, dq_model.name
        """

        try:
            results = self.execute_neo4j_query(query)
            return_info = {}
            if results:
                for record in results:
                    dq_model_id = record.get('dq_model.id')
                    dq_model_name = record.get('dq_model.name')
                    if dq_model_id and dq_model_name:
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

    async def get_applied_methods_by_dq_model(self, dq_model_id):
        methodName = "Method2"
        query = f"""
            MATCH path = (dq_model:DQModel {{id: '{dq_model_id}'}})
            -[:HAS_APPLIED_DQ_METHOD]->(applied:AppliedDQMethod)
            -[:APPLIED_TO]->(startNode:Field)
            -[:belongsToField*0..]->(endNode)-[:belongsToSchema]->(col:Collection) 
            WHERE EXISTS {{
                MATCH (applied)-[:APPLIES_METHOD]->(method:Method {{name: '{methodName}'}})}}            
            WITH endNode, applied, path, size([rel IN relationships(path) WHERE type(rel) = 'belongsToField']) AS depth
            ORDER BY depth DESC
            WITH endNode, applied, collect(path)[0] AS longest_path

            OPTIONAL MATCH (applied)-[:MODEL_MEASURE]->(measure:Measure)<-[:FieldMeasure]-(field:Field)

            RETURN nodes(longest_path)[1..] AS nodes, 
                relationships(longest_path) AS relationships, 
                COLLECT(DISTINCT measure) AS measures
            """
        
        try:
            records, _, _ = self.neo4j_driver.execute_query(query)
            results = []
            for record in records:
                nodes = record[0]
                measures = record["measures"]
                attribute_path_list = []
                attribute_measures = []

                for measure in measures:
                    attribute_measures.append({"date": measure["date"], "measure": measure["measure"]})

                for node in nodes[1:len(nodes)-1]:
                    attribute_path_list.insert(0, node['name'])

                attribute_path = "-".join(attribute_path_list)
                field_node = FieldNode(
                    element_id=nodes[1].element_id,
                    name=attribute_path,
                    type=nodes[1]['type'],
                    measures=attribute_measures
                )
                results.append(field_node)
            return results
        except Exception as e:
            print("Error executing query:", e)
            return None

    async def get_data_quality_rules(self):
        try:
            query = """
                MATCH (d:Dimension)<-[:HAS_DIMENSION]-(f:Factor)<-[:HAS_FACTOR]-(m:Metric)<-[:HAS_METRIC]-(me:Method)
                RETURN d.name AS dimension, f.name AS factor, m.granularity AS granularity, me.id AS method_id
            """
        
            result, _, _ = self.neo4j_driver.execute_query(query)
            data_structure = {}

            for record in result:
                dimension = record["dimension"]
                factor = record["factor"]
                granularity = record["granularity"]
                method_id = record["method_id"]

                if dimension not in data_structure:
                    data_structure[dimension] = {"dimension": dimension, "factors": {}}

                if factor not in data_structure[dimension]["factors"]:
                    data_structure[dimension]["factors"][factor] = {
                        "name": factor,
                        "metrics": []
                    }

                current_factor = data_structure[dimension]["factors"][factor]
                if granularity == "value":
                    current_factor["metrics"].append({
                        "method_id": method_id,
                        "name": f"Metric {len(current_factor['metrics']) + 1}"
                    })

            final_data = []
            for dimension_data in data_structure.values():
                dimension_data["factors"] = list(dimension_data["factors"].values())
                final_data.append(dimension_data)

            return final_data

        except Exception as e:
            print("Error executing query:", e)
            raise Exception("Error executing query")

    def get_last_node_in_nested_fields_query(self, json_schema_id: str, dq_model_id: str, json_keys: List[str]) -> str:
        first_key = json_keys[0]
        last_key = json_keys[-1]
        graph_path = f"""
            MATCH (c:Collection {{id_dataset: '{json_schema_id}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})        
        """

        for key in json_keys[1:]:
            node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
            graph_path += node_path

        query = f"""
            {graph_path}
            MERGE (applied_dq_method:AppliedDQMethod {{name: 'applied_dq_f{last_key}'}})                
            MERGE (applied_dq_method_col:AppliedDQMethod {{name: 'applied_dq_f{last_key}col'}})                
            MERGE (applied_dq_method)-[:APPLIED_TO]->(f{last_key})
            MERGE (applied_dq_method_col)-[:APPLIED_TO]->(f{last_key})
            MERGE (dq_method)-[:APPLIED_IN]->(applied_dq_method)
            MERGE (dq_method_col)-[:APPLIED_IN]->(applied_dq_method_col)
            MERGE (dq_model)-[:HAS_APPLIED_DQ_METHOD]->(applied_dq_method)
            MERGE (dq_model)-[:HAS_APPLIED_DQ_METHOD]->(applied_dq_method_col)
        """
        return query

    def get_dq_model(self, ontology_id: str, json_schema_id: str, mapped_entries: List[str]) -> str:
        query = f"""
            MATCH (dq_model:DQModel)-[:MODEL_CONTEXT]->(context:Context {{id: '{ontology_id}'}})
            MATCH (dq_model)-[:MODEL_DQ_FOR]->(collection:Collection {{id_dataset: '{json_schema_id}'}})
            RETURN dq_model.id as id
        """
        try:
            result, _, _ = self.neo4j_driver.execute_query(query)
            if result:
                return result[0]["id"]
            return None
        except Exception as e:
            print("error in executing query: ", e)
            return None

    async def save_data_quality_model(self, dto: SaveDQModelDTO) -> str:
        """Save a data quality model using the provided DTO.
        
        Args:
            dto: Data transfer object containing all necessary information to create a DQ model.
            
        Returns:
            str: The ID of the created or existing DQ model.
        """
        print("### Starting save data quality model process in neo4j ###")
        print("### Model dq entries : ###", dto.mapped_entries)
        mapping_process_docu = dto.mapping_process_docu
        ontology_id = mapping_process_docu.ontologyId
        json_schema_id = mapping_process_docu.jsonSchemaId
        dq_model_id = str(uuid.uuid4())
        timestamp_milliseconds = int(time.time() * 1000)

        print("##First check if dq model with same context, dataset and appliedDqMethod's exists")
        dq_model_already_exists = self.get_dq_model(ontology_id, json_schema_id, dto.mapped_entries)
        if (dq_model_already_exists):
            print("DQ Model already exists, with the info: ", dq_model_already_exists)
            print("#########")
            return dq_model_already_exists

        print(" ## METHOD ID: ", dto.dq_method_id)
        print(" ## METHOD ID AGG: ", dto.dq_aggregated_method_id)

        query = f""" 
            MATCH (dq_method:Method {{id: '{dto.dq_method_id}'}})
            MATCH (dq_method_col:Method {{id: '{dto.dq_aggregated_method_id}'}})
            MERGE (context:Context {{name: 'context', id: '{ontology_id}'}})
            MERGE (collection:Collection {{id_dataset: '{json_schema_id}'}})
            MERGE (dq_model:DQModel  {{name: '{dto.dq_model_name}', id: '{dq_model_id}', mapping_process_id: '{dto.mapping_process_id}'}})
            MERGE (dq_model)-[:MODEL_CONTEXT]->(context)
            MERGE (dq_model)-[:MODEL_DQ_FOR]->(collection)
            MERGE (context)-[:DATASET_CONTEXT]->(collection)
        """
        
        for attribute in dto.mapped_entries:
            print("attribute mapped: ", attribute)
            json_keys = find_json_keys(attribute)
            print("json keys: ", json_keys)
            query += " WITH collection, dq_model, dq_method, dq_method_col"
            add_applied_method_query = self.get_last_node_in_nested_fields_query(json_schema_id, dq_model_id, json_keys)
            print("add_applied_method_query: ", add_applied_method_query)
            query += add_applied_method_query
       
        print("### Query for creating dq model ###", query)
        try:
            self.neo4j_driver.execute_query(query)
            return dq_model_id
        except Exception as e:
            print("error in executing query: ", e)
            return None