from typing import Dict, Any, List
from datetime import datetime
import uuid
import time
from collections import defaultdict

from app.database import get_neo4j_driver
from app.models.mapping import FieldNode
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

        delete_existing_measures = f"""
            {graph_path}
            MATCH (f{latest_item})-[r:FieldValueMeasure]->(m:Measure)
            DETACH DELETE m
        """

        print("DELETE QUERY: ", delete_existing_measures)
        self.neo4j_driver.execute_query(delete_existing_measures)

    async def insert_field_value_measures(self, field: FieldNode, value, id_document, dq_model_id, node_name):
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
        self.neo4j_driver.execute_query(insert_measure_query)

    async def insert_field_measures(self, field: FieldNode, node_name, value, dq_model_id):
        print("LAST ITEM: ", node_name)
        current_datetime = datetime.now()

        applied_dq_method_name = f"applied_dq_f{node_name}col" # TODO: agregar _col / o cambiar a _aggregated 
        print("searching for: ", applied_dq_method_name)
        print("About to insert field measure for: ", field.element_id)

        query = f"""
            MATCH (fieldNode) 
            WHERE elementId(fieldNode) = '{field.element_id}' 
            MATCH (fieldNode)<-[:APPLIED_TO]-(appliedMethod:AppliedDQMethod {{name: '{applied_dq_method_name}'}})<-[:HAS_APPLIED_DQ_METHOD]-(dq_model:DQModel {{id: '{dq_model_id}'}})
            CREATE (m:Measure)<-[:FieldMeasure]-(fieldNode)
            CREATE (m)<-[:MODEL_MEASURE]-(appliedMethod)
            SET m.measure = {value}, m.date= '{current_datetime}'
        """

        print("## QUERY ##", query)
        self.neo4j_driver.execute_query(query)

    async def get_evaluation_results_v2(self, data_model_id, json_schema_id, json_keys, limit, offset):
        first_key = json_keys[0]
        graph_path = f"""
            MATCH (dq:DQModel {{id: '{data_model_id.strip()}'}})            
            -[:MODEL_DQ_FOR]->(c:Collection {{id_dataset: '{json_schema_id}'}})
            <-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})        
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

        print("## QUERY ##", query)
        print("## COUNT QUERY ##", count_query)

        try:
            result, _, _ = self.neo4j_driver.execute_query(query)
            count_result, _, _ = self.neo4j_driver.execute_query(count_query)
            total_count = count_result[0].get('total')
            print("## RESULT ##", result)
            print("## TOTAL COUNT ##", total_count)
            return result, total_count
        except Exception as e:
            print("Error executing query:", e)
            return None

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
        match_query = """
            MATCH (d:Dimension)<-[:HAS_DIMENSION]-(f:Factor)<-[:HAS_FACTOR]-(m:Metric)<-[:HAS_METRIC]-(me:Method)
            RETURN d.name AS dimension, f.name AS factor, m.granularity AS granularity, me.id AS method_id
        """
        result, _, _ = self.neo4j_driver.execute_query(match_query)

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

    def get_last_node_in_nested_fields_query(self, json_schema_id: str, dq_model_id: str, json_keys: List[str]) -> str:
        first_key = json_keys[0]
        graph_path = f""" 
            MATCH (collection)<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
        """
        last_node = "f"+ first_key
        for key in json_keys[1:]:
            node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
            graph_path += node_path
            last_node = "f"+ key

        applied_dq_name = "applied_dq_" + last_node
        applied_dq_name_col = "applied_dq_" + last_node + "col"
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

    mapping_type_separator = "?"

    async def get_dq_model(self, ontology_id: str, json_schema_id: str, attributes_mapped: List[str]) -> str:
        """Check if a DQ model exists for the given context, dataset and mapped attributes.
        
        Args:
            ontology_id: ID of the ontology (context)
            json_schema_id: ID of the JSON schema (dataset)
            attributes_mapped: List of mapped attributes to check
            
        Returns:
            str: ID of the existing DQ model if found, None otherwise
        """
        looked_fields = []
        for attribute in attributes_mapped:
            attr_keys = attribute.split(self.mapping_type_separator)[0]
            attr_keys = '-'.join(attr_keys.split('-')[1:])
            looked_fields.append(attr_keys)
            print("attr_keys: ", attr_keys)

        query = f"""
            MATCH (ctx:Context {{id: '{ontology_id}'}})<-[:MODEL_CONTEXT]-(dq_model:DQModel)
            -[:MODEL_DQ_FOR]->(ds:Collection {{id_dataset: '{json_schema_id}'}})
            RETURN dq_model.id, dq_model.name
        """
        print("#query for checking if dq model exist#: ", query)
        print("Looked Fields: ", looked_fields)

        try:
            records, _, _ = self.neo4j_driver.execute_query(query)
            if records:
                for record in records:
                    dq_model_id = record.get('dq_model.id')
                    # Get applied methods for this model
                    applied_methods = await self.get_applied_methods_by_dq_model(dq_model_id)
                    if applied_methods:
                        # Get field names from applied methods
                        applied_fields = [method.name for method in applied_methods]
                        counter_looked = len(looked_fields)
                        counter_applied = len(applied_fields)
                        # Check if both lists have the same length and all looked fields are in applied fields
                        if counter_looked == counter_applied and all(field in applied_fields for field in looked_fields):
                            return dq_model_id
                return None
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
        mapping_process_docu = dto.mapping_process_docu
        ontology_id = mapping_process_docu.ontologyId
        json_schema_id = mapping_process_docu.jsonSchemaId
        dq_model_id = str(uuid.uuid4()) # ver que hacemos con esto
        timestamp_milliseconds = int(time.time() * 1000)

        dq_model_already_exists = await self.get_dq_model(ontology_id, json_schema_id, dto.mapped_entries)
        if (dq_model_already_exists):
            print("DQ Model already exists, with the info: ", dq_model_already_exists)
            return dq_model_already_exists

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