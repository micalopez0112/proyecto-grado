from owlready2 import get_ontology, locstr
from typing import Dict, Any
from abc import ABC, abstractmethod
from bson import ObjectId
import json

from app.database import mapping_process_collection, onto_collection
from app.dq_evaluation.mocks import get_hardcoded_test_documents
from app.models.mapping import MappingProcessDocument,DQModel, FieldNode
from app.models.ontology import OntologyDocument
from app.rules_validation.mapping_rules import getOntoPropertyByIri, getJsonSchemaPropertieType
from app.repositories import mapping_repo, metadata_repo
from ..database import  get_neo4j_driver

neo4j_driver = get_neo4j_driver()
# TODO code-quality: mover estas constantes
SYNTCTATIC_ACCURACY = "syntactic_accuracy"
QUALITY_RULES = [SYNTCTATIC_ACCURACY]
AGG_AVERAGE = "average"
class QualityMetric(ABC) : 

    def __init__(self, aggregation) -> None:
        self.mapping_process_id: str = ""
        self.mapping_process: MappingProcessDocument = None
        self.dq_model_id: str = ""
        self.dq_model: DQModel = None
        self.aggregation = aggregation
        pass
    
    async def evaluation(self) -> None :
        data = self.get_data_to_evaluate()
        print("## Evaluacion 3.0 - got data to be evaluated")
        result = await self.execute_measure(data)
        return result

    @abstractmethod
    def get_data_to_evaluate(self) -> None : 
        pass

    @abstractmethod  
    async def execute_measure(self, data) :    
        pass
    
    async def set_mapping_process(self, dq_model_id: str) -> None:
        pass
    
    def set_dq_model_id(self, dq_model_id: str) -> None:
        pass
    
    # calculate_aggregated_measure serves to calculate the aggregated measure according to the agreggation selected
    def calculate_aggregated_measure(self, field_measures_list):
        print("aggregation setted", self.aggregation)
        if self.aggregation == AGG_AVERAGE:
            print("About to calculate aggregated average")
            aggregated_measure_value = sum(field_measures_list) / len(field_measures_list)
            return aggregated_measure_value
            

class SyntanticAccuracy(QualityMetric) :
    
    def set_dq_model_id(self, dq_model_id: str) -> None:
        self.dq_model_id = dq_model_id

    async def set_mapping_process(self, dq_model_id: str) -> None:
        # necesito obtener el mapping_process_id a partir del dq_model
        print("## Evaluacion 1.1 - get mapping id by dq model with dq id : ", dq_model_id, " ##")
        mapping_procces_id = metadata_repo.get_mapping_id_by_dq_model(dq_model_id)
        mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_procces_id))
        self.mapping_process = mapping_process

    async def execute_measure(self, data_to_evaluate) :
        # ver ss movemos esto
        # esto muevo para otro lado
        print("## Evaluacion 4.0 - about to start evaluation mapping_process: ")
        dq_model_id = self.dq_model_id
        ontology = await get_onto(self.mapping_process.ontologyId)
        jsonSchemaId = self.mapping_process.jsonSchemaId
        print("## Evaluacion 4.1 - jsonSchemaId: ", jsonSchemaId) #self.mapping_elements)
        applied_to_fields = metadata_repo.get_applied_methods_by_dq_model(dq_model_id)
        mapping_elements = self.mapping_process.mapping

        results_dicc = {}
        print("## Evaluacion 4.2 - mapping elements: ", mapping_elements)
        for field_to_evaluate in applied_to_fields:
            print("## Evaluacion 4.3 - mapping elements:  ", field_to_evaluate.name)

            json_mapped_key = build_mapping_entrance(field_to_evaluate)
            print("## Evaluacion 4.4 - json mapped key  ", json_mapped_key)
            onto_mapped_to_value = mapping_elements[json_mapped_key]
            
            print("## Evaluacion 4.5 - onto mapped to", onto_mapped_to_value)
            results_for_mapped_entrance = self.evaluate_instances(dq_model_id, data_to_evaluate, field_to_evaluate, onto_mapped_to_value, ontology, jsonSchemaId)
            results_dicc[json_mapped_key] = results_for_mapped_entrance
            
        print("##---- Evaluation results: ", results_dicc, " ----##")
        return results_dicc
        
    # def evaluate_instances(json_instances, onto_mapped_to_value, ontology, jsonSchemaId) :
    def evaluate_instances(self, dq_model_id, json_instances, field_to_evaluate, onto_mapped_to_value, ontology, jsonSchemaId) :
        json_mapped_key = build_mapping_entrance(field_to_evaluate)
        print("## Evaluacion 4.5.1 - onto mapped to", json_mapped_key, "###")
        print("## Evaluacion 4.5.2 - onto mapped to", len(json_instances))
        results_dicc = {}
        index = 1   # algo temporal
        field_measures = []
        json_keys = find_json_keys(json_mapped_key)
        print("## Evaluacion 4.5.3 - json keys", json_keys)

        # TODO: retomar y arreglar implementación del delete
        #metadata_repo.delete_existing_field_value_measures(json_keys, jsonSchemaId)
        
        # se evalua cada una de las intancias json
        for json_instance in json_instances :
            print("## Evaluacion 4.5.4 - json keys", json_instance)
            result_key = json_mapped_key + "_" + str(index)
            print("## Evaluacion 4.5.5 - result key", result_key)
            index = index + 1
            
            element = find_element_in_JSON_instance(json_instance, json_mapped_key)
            print("## Evaluacion 4.5.6 - found element", element)
            if element is None:
                value = 0

            # si esta OK en alguna de los ontologias a la cual haya mapeado se toma como que es válido
            for onto_mapped_to in onto_mapped_to_value:
                print("## Evaluacion 4.5.7 - onto value", onto_mapped_to['iri'])
                onto_prop = getOntoPropertyByIri(onto_mapped_to['iri'], list(ontology.data_properties()))
                instances = list(onto_prop.get_relations())
                print("## Evaluacion 4.5.8 - onto instances", instances, " ##")
                ## instancias de las clases de la ontología
                for onto_inst in instances:
                    dp_value = onto_inst[1]
                    if(isinstance(dp_value, locstr)):
                        dp_value = str(dp_value)

                    value = compare_onto_with_json_value(dp_value, element)
                    print("## Evaluacion 4.5.8 - evaluation result", value, " ##")
                    if value == 1:
                        break
            field_measures.append(value)

            print("## Evaluacion 4.6 - insert value in neo4j", value, " ##")
            metadata_repo.insert_field_value_measures_v2(field_to_evaluate, value, json_instance['id'], dq_model_id)
            results_dicc[result_key] = value

        #almacena un FieldMeasure por corrida, asi manetemos el historicos del las corridas
        # Aggregate all field measures and insert the result
        if field_measures:
            aggregated_measure_value = self.calculate_aggregated_measure(field_measures)
            print("Aggregated", aggregated_measure_value,)
            metadata_repo.insert_field_measures(json_keys, aggregated_measure_value, jsonSchemaId)

        # ver: pero de alguna forma devolver solo el resultado agregado
        return aggregated_measure_value
    
    # si todas las evaluaciones se van a basar en mapeos json esto se puede mover para la clase principal QualityMetric
    # get_data_to_evaluate gets the instances to be evaluated from the document storage path
    def get_data_to_evaluate(self) : 
        print("## SyntanticAccuracy: get_data_to_evaluate ##")
        storage_path = self.mapping_process.document_storage_path   
        JSONInstances = get_documents_from_storage(storage_path)

        print("## SyntanticAccuracy: Got json instances correctly ##")
        return JSONInstances
    
# this functions receives the attribute_path 'contacto-nombre' and builds the proper json key to find
# the value in the mapping document, adding the missing "rootObject", "key" and "type"
def build_mapping_entrance(attribute_field: FieldNode):
    print("Field node: ", attribute_field)
    return "rootObject-" + attribute_field.name + "_key#" + attribute_field.type   

    
class StrategyContext():
    def __init__(self) -> None:
        pass

    @property
    def quality_strategy(self) -> QualityMetric:
        return self._quality_strategy

    @quality_strategy.setter
    def strategy(self, strategy: QualityMetric) -> None:
        self._quality_strategy = strategy

    def select_strategy(self, strategy: str, aggregation: str) -> None:
        if strategy == SYNTCTATIC_ACCURACY:
            self._quality_strategy = SyntanticAccuracy(aggregation) 
            print("### STRATEGY METHOD SELECTED ## ")
                    
    async def evaluate_quality(self, dq_model_id: str) -> None:
        # no se si vamos a menter esto o mandamos el mapping id como parametro siempre VER
        try:
            if dq_model_id != "" and dq_model_id != None :
            # ver si queda aca o lo mando por parametro al contstructor
                print("## Evaluacion 1.0 - about to se mapping process", dq_model_id)
                await self.quality_strategy.set_mapping_process(dq_model_id)
                self.quality_strategy.set_dq_model_id(dq_model_id)
                print("## Evaluacion 2.0 - mapping process setted")
                result = await self._quality_strategy.evaluation()
                return result
            else:
                print("###  SOMETHING IS WRONG DQ_MODEL_ID CANT BE NONE ###")
        except Exception as e:
            print(f"Error: {e}")
            return e

# mover para otro lado
async def get_onto(ontology_id: str) :
    onto_id = ObjectId(ontology_id)
    ontology_docu = await onto_collection.find_one({'_id': onto_id})
    ontology_document = OntologyDocument(**ontology_docu)
    ontology_path = ontology_document.uri
    if ontology_document.type == "FILE":
        ontology_path = ontology_document.file
    
    ontology = get_ontology(ontology_path).load()
    return ontology

# this function will access the storage and get the documents
# we need to define the storage service or how we will access it
def get_documents_from_storage(path : str) :
    print(f"Document storage path received {path}")
    print(f"Getting documents from storage")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"Data loaded from storage successfully")
    #data = get_hardcoded_test_documents()
    return data

# esta función busca un elemento en un json a partir de un path dado por la entrada del mapping
# destination-accomodation-name
# accomodation aca puedo recibir value
# TODO: ver posibilidad de obtener el nodo FIELD, aprovechando la anidación entre los campos del json
def find_element_in_JSON_instance(json_document, path) :
    print(f'json_document ${json_document}')
    print(f'path ${path}') #contacto-city_key#string
    keys = path.replace('-', '_').split('_')
    for key in keys:
        print(key)
    print(f'keys ${keys}')

    json_keys = keys[:-1] 
    json_keys.remove('rootObject')
    element = json_document
    try:
        for key in json_keys:
            element = element[key]
        return element
    except (KeyError, TypeError):
        return None

# find_json_keys gets the key of a mapping structure for example "#contacto-city_key#string", and returns 
# a lis of the json keys of that entry: ['contacto','city'], this means that 'city' its an attribute inside 'contacto'
def find_json_keys(path) :
    print(f'path ${path}') #contacto-city_key#string
    keys = path.replace('-', '_').split('_')
    for key in keys:
        print(key)
    print(f'keys ${keys}')

    # json_keys = ['contacto', 'city']
    json_keys = keys[:-1] 
    json_keys.remove('rootObject')
    return json_keys

def compare_onto_with_json_value(onto_prop_value, json_value) :
    # hacer un toLower() aca o
    print("## Syntactic Accuracy: compare_onto_with_json_value onto:", onto_prop_value," json:", json_value,"##")
    if onto_prop_value == json_value:
        return 1
    return 0 