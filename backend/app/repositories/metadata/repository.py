from typing import Dict, Any, List
from datetime import datetime, date
import uuid
from collections import defaultdict

import pandas as pd
from pathlib import Path
from unidecode import unidecode

from app.database import get_neo4j_driver
from app.models.mapping import FieldNode
from app.rules_validation.mapping_rules import find_json_keys
from app.repositories.metadata.types import SaveDQModelDTO, DqResultDTO



class MetadataRepository:
    def __init__(self, neo4j_driver=None):
        self.neo4j_driver = neo4j_driver or get_neo4j_driver()
        self.current_directory = Path(__file__).resolve().parent
        self.zone = "trusted"

    def set_neo4j_driver(self, new_neo4j_driver):
        self.neo4j_driver = new_neo4j_driver

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

        self.neo4j_driver.execute_query(delete_existing_measures)

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

        applied_dq_method_name = f"applied_dq_f{node_name}col" # TODO: agregar _col / o cambiar a _aggregated 


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
        graph_path = f"""MATCH (dq:DQModel {{id: '{data_model_id.strip()}'}})
            -[:MODEL_DQ_FOR]->(c:Collection {{id_dataset: '{json_schema_id.strip()}'}})<-[:belongsToSchema]-(f{first_key}:Field{{name: '{first_key}'}})
        """
        
        for key in json_keys[1:]:
            node_path = f"<-[:belongsToField]-(f{key}:Field{{name: '{key}'}})"
            graph_path += node_path

        latest_item = json_keys[-1]
        count_query = f"""
            {graph_path}-[fvm:FieldValueMeasure]->(measure)
            RETURN COUNT(*)
        """
        neo4j_driver = get_neo4j_driver()
        count_result, _, _ = neo4j_driver.execute_query(count_query)
        total_count = count_result[0][0] if count_result else 0  # Extraer el total de la consulta

        select_measure = f"""
            {graph_path}-[fvm:FieldValueMeasure]->(measure)
            RETURN f{latest_item}, measure, fvm
            SKIP {offset} 
            LIMIT {limit}
        """
        
        records, _, _ = neo4j_driver.execute_query(select_measure)
        results = []
        for record in records:
            dq = DqResultDTO(name=record[0]['name'], id_document=record[2]['id_document'], 
                        date=record[1]['date'], 
                        measure=record[1]['measure'])
            results.append(dq)

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
            return return_info
        except Exception as e:
            print("Error in executing query: ", e)
            raise e

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
            raise e

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

        query = f"""
            MATCH (ctx:Context {{id: '{ontology_id}'}})<-[:MODEL_CONTEXT]-(dq_model:DQModel)
            -[:MODEL_DQ_FOR]->(ds:Collection {{id_dataset: '{json_schema_id}'}})
            RETURN dq_model.id, dq_model.name
        """

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
        try:
            mapping_process_docu = dto.mapping_process_docu
            ontology_id = mapping_process_docu.ontologyId
            json_schema_id = mapping_process_docu.jsonSchemaId
            dq_model_id = str(uuid.uuid4())

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
                query += " WITH collection, dq_model, dq_method, dq_method_col"
                add_applied_method_query = self.get_last_node_in_nested_fields_query(json_schema_id, dq_model_id, json_keys)
                query += add_applied_method_query
        
            self.neo4j_driver.execute_query(query)
            return dq_model_id
        except Exception as e:
            print("Error in executing query: ", e)
            raise e
        
 
    def init_governance_zone(self):
        ## Hardcoded specific dimension, factor and metric for this project
        try:
            print("Going to init governance zone")
            self.save_quality_dimension()
            self.save_quality_factor()
            self.save_quality_metrics()
            self.save_quality_methods()
            print("Finished init governance zone")
        except Exception as e:
            print("Error in init governance zone: ", e)
            raise e

    def save_quality_dimension(self):
    # print("Se va a ejecutar save_quality_dimension")
        current_directory = Path(__file__).resolve().parent
        dimensions_file_path = current_directory / "quality_data/dq_dimensions.csv"
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
        self.neo4j_driver.execute_query(query)
    
    def save_quality_factor(self):
        
        current_directory = Path(__file__).resolve().parent
        factor_file_path = current_directory / "quality_data/dq_factors.csv"
        factor_ds = pd.read_csv(factor_file_path);
        
        query_template = """
            MERGE ({factor_var_name}:Factor {{name: '{factor_name}', id:'{factor_id}'}})
            MERGE ({factor_var_name})-[:HAS_DIMENSION]->(dim)
        """
        
        query = ''
        previous_dimension = ''
        for index, row in factor_ds.iterrows():
            
            if (row['dimension_id'] != previous_dimension):
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

            # TODO-pau: ver esto
            factor_var_name = unidecode(row['name'].lower().replace(' ', "_").replace('-','_'))
            
            query += query_template.format(
                factor_name=row['name'],
                factor_var_name=factor_var_name,
                factor_id=row['factor_id'],
                dimension_id=row['dimension_id']
            )
            
            previous_dimension = row['dimension_id']
        self.neo4j_driver.execute_query(query)
        
    def save_quality_metrics(self):
        neo4j_driver = get_neo4j_driver()
        metrics_file_path = self.current_directory / "quality_data/dq_metrics.csv"
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
        self.neo4j_driver.execute_query(query)

    def save_quality_methods(self):
        neo4j_driver = get_neo4j_driver()
        methods_file_path = self.current_directory / "quality_data/dq_methods.csv"
        methods = pd.read_csv(methods_file_path);
        
        query_template = """        
            MERGE ({method_var_name}: Method {{id:'{method_id}',name:'{method_name}', description: '{method_description}', algorithm: '{method_algorithm}'}})
            MERGE ({method_var_name})-[:HAS_METRIC]->(metric)
        """

        query = ''
        previous_metric = ''
        for index, row in methods.iterrows():
            
            if (row['metric_id'] != previous_metric):
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

        self.neo4j_driver.execute_query(query)

    def generate_metadata_from_schema(self, collection_path:str,schema: Dict[str, Any], id_dataset: str):
        today_date = date.today()
        ## Asumimos que los metadatos están disponibles para ser creados en la Ingestion Zone => date = today
        collection_name = schema.get("collection_name")
        collection_query = self.get_collection_query()
        params = {
            'collection_name': collection_name,
            'ingestion_date': today_date,
            'collection_path': collection_path,
            'zoneName': self.zone,
            'id_dataset' : id_dataset
        }
        collection_insert_result = self.execute_neo4j_query(collection_query, params)

        collection_node = collection_insert_result[0]
        collection_node_id = collection_node['collectionElementId']
        print(f'El elementId con el que se insertó la colección es: {collection_node_id}')
        schema_properties = schema.get("properties")
        ##Creamos los fields del schema
        for field_key, field_value in schema_properties.items():
            try:
                self.generate_fields_metadata(collection_node_id, "schema", field_key, field_value)  
            except Exception as e:
                print(f"Error al crear el field {field_key}: {e}")
    #    return collectionNodeId

    ##parentType = "schema" | "field" 
    def generate_fields_metadata(self, parent_node_Id:str, parent_type:str, field:str, field_value: Dict[str, Any]):
        try:
            field_type = field_value.get("type")
            belongs_to = "belongsToField"
            if parent_type == "schema":
                belongs_to = "belongsToSchema"

            field_query = self.get_field_query(belongs_to)
            params = {
                'parentNodeId': parent_node_Id,
                'fieldName': field,
                'fieldType': field_type,
                'parentType': parent_type.capitalize(),  # Capitalizamos aquí para la relación
                'belongsTo': belongs_to
            }
        
            field_insert_result = self.execute_neo4j_query(field_query, params)
            field_node = field_insert_result[0]           
            field_node_id = field_node['fieldElementId']

            # Si el field es un objeto, recorrer sus propiedades de forma recursiva
            if field_type == "object":
                properties = field_value.get("properties", {})
                for sub_field_key, sub_field_value in properties.items():
                    # Recursión: El campo padre ahora será el field que acabamos de crear
                    self.generate_fields_metadata(field_node_id, "field", sub_field_key, sub_field_value)
            elif field_type == "array":
                itemValue = field_value.get("items")
                self.generate_fields_metadata(field_node_id, "field", "items",itemValue )
        
        except Exception as e:
            print(f"Error al crear el NODO para field {field}: {e}")

    def get_field_query(self, belongs_to):
        #autogenerate fieldId
        fieldId = str(uuid.uuid4())
        return f"""
                MATCH (parent) WHERE elementId(parent) = $parentNodeId
                CREATE (field:Field {{
                    id_field: '{fieldId}',
                    name: $fieldName,
                    type: $fieldType
                }})
                CREATE (field)-[:{belongs_to}]->(parent)
                SET field += {{ parentType: $parentType }}
                RETURN elementId(field) AS fieldElementId
            """

    def get_collection_query(self):
        return """
            MERGE (zone:Zone { name: $zoneName })
            CREATE (collection:Dataset:Collection {
                name: $collection_name,
                description: "Colección que contiene información sobre varias películas",
                ingestion_date: $ingestion_date,
                ingestion_info: $collection_path,
                type: "json file",
                id_dataset: $id_dataset
            })
            WITH collection, zone
            CREATE (collection)-[:STOREDIN]->(zone)
            RETURN elementId(collection) AS collectionElementId
        """
    # TODO completar
    def insert_context_metadata(self, ontology_id, onto_name):
        print("Inserting context with new implementation")
        query = f"""
            MERGE (ctx:Context {{name:'{onto_name}',id: '{ontology_id}'}})
        """
        self.neo4j_driver.execute_query(query)
    
    def get_mapping_id_by_dq_model(self, dq_model_id: str):
        match_query = f"""
            MATCH (dq:DQModel  {{id: '{dq_model_id}'}}) 
            return dq.mapping_process_id as mapping_process_id
        """
        result, _, _ = self.neo4j_driver.execute_query(match_query)
        #     neo4j_driver = get_neo4j_driver()
        # result, _, _ = neo4j_driver.execute_query(match_query)
        print("RESULT: ",result[0]['mapping_process_id'])
        return result[0]['mapping_process_id']

    def delete_existing_field_value_measures(self, data_model_id, json_keys, json_schema_id):
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


   
        