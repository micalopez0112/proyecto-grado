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
from ..database import  neo4j_driver

SYNTCTATIC_ACCURACY = "syntactic_accuracy"
QUALITY_RULES = [SYNTCTATIC_ACCURACY]

class QualityMetric(ABC) : 
    async def evaluation(self) -> None :
        data = self.get_data_to_evaluate()
        print("## Evaluacion 3.0 - got data to be evaluated")
        result = await self.execute_measure(data)
        # ver si sacamos esto poruqe no esta haciendo nada
        await self.save_result(result) # esto capaz se mueve para execute_measure y se guarda enseguida que se calcula
        return result

    @abstractmethod
    def get_data_to_evaluate(self) -> None : 
        pass

    @abstractmethod  
    async def execute_measure(self, data) :    
        pass
    
    @abstractmethod
    async def save_result(self, result) -> None :     
        pass

    async def set_mapping_process(self, dq_model_id: str) -> None:
        pass
    
    def set_dq_model_id(self, dq_model_id: str) -> None:
        pass

    def set_mapping_elements(self, mapping_elems:  Dict[str, Any]) -> None:
        pass

class SyntanticAccuracy(QualityMetric) :
    def __init__(self) -> None:
        self.mapping_process_id: str = ""
        self.mapping_process: MappingProcessDocument = None
        #self.mapping_elements:  Dict[str, Any] = {}
        self.dq_model_id: str = ""
        self.dq_model: DQModel = None
        pass
    
    def set_dq_model_id(self, dq_model_id: str) -> None:
        self.dq_model_id = dq_model_id
    # TODO: borrar este metodo
    async def set_mapping_process(self, dq_model_id: str) -> None:
        # necesito obtener el mapping_process_id a partir del dq_model
        print("## Evaluacion 1.1 - get mapping id by dq model with dq id : ", dq_model_id + " ##")
        mapping_procces_id = metadata_repo.get_mapping_id_by_dq_model(dq_model_id)
        mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_procces_id))
        #print("## Evaluacion 1.2 - get got mapping_process : ", mapping_process + " ##")
        self.mapping_process = mapping_process
        #print("## Evaluacion 1.3 - setted mapping_process : ", mapping_process + " ##")

    
    # async def set_dq_model(self, dq_model_id: str) -> None:
    #     print("## Iniciating SyntaticAccuracy with mp id : ", dq_model_id + " ##")
    #     # aca hago una query y me traigo el dq model
    #     # mapping_process = await mapping_repo.find_mapping_process_by_id(ObjectId(mapping_process_id))
    #     self.dq_model = dq_model

    # def set_mapping_elements(self, mapping_elems:  Dict[str, Any]) -> None:
    #     print("## SyntanticAccuracy: set_mapping_elements ##", mapping_elems)
    #     self.mapping_elements = mapping_elems

    async def execute_measure(self, data_to_evaluate) :
        # ver ss movemos esto
        # esto muevo para otro lado
        print("## Evaluacion 4.0 - about to start evaluation mapping_process: ")
        dq_model_id = self.dq_model_id
        ontology = await get_onto(self.mapping_process.ontologyId)
        jsonSchemaId = self.mapping_process.jsonSchemaId
        print("## Evaluacion 4.1 - jsonSchemaId: ", jsonSchemaId) #self.mapping_elements)
        results_dicc = {}
        # OPCIONES PARA ESTE FOR
        # (1): me traigo todo los applied dq method del dq model, saco toda la traza del field (street-contacto)
        #  armo los mapping items y mantengo como esta, hay que ver al momento de evaluar
        #  tengo que buscar de nuevo el nodo donde asignar la measure
        #

        #   
        # (2): recorro los appliedMethods, para cada uno armo la cadena de street-contacto
        #  evaluo
        # necesito agregar el mapping_id al dq_model
        # me traigo todos los applied_dq_method junto con los fields
        # lo plancho a la traza--- pero tambien me quedo con el id
        # y cuando voy a hacer el insert lo hago con el id, ver si funciona
        # guardo el resultado ver como pero capaz es mas directo teniendo ya cual es el nodo tecnicamente
        applied_to_fields = metadata_repo.get_applied_methods_by_dq_model(dq_model_id)
        mapping_elements = self.mapping_process.mapping
        print("## Evaluacion 4.2 - mapping elements: ", mapping_elements)
        for field_to_evaluate in applied_to_fields:
            print("## Evaluacion 4.3 - mapping elements:  ", field_to_evaluate.name)

            json_mapped_key = build_mapping_entrance(field_to_evaluate)
            print("## Evaluacion 4.4 - json mapped key  ", json_mapped_key)
            # ver de donde sale mapping elements
            onto_mapped_to_value = mapping_elements[json_mapped_key]
            

            print("## Evaluacion 4.5 - onto mapped to", onto_mapped_to_value)
            results_for_mapped_entrance = evaluate_json_instances(data_to_evaluate, field_to_evaluate, json_mapped_key, onto_mapped_to_value, ontology, jsonSchemaId)
            results_dicc[json_mapped_key] = results_for_mapped_entrance
            # TODO: ver pero creo que aca ya no es mas necesario ver si el mapping es una


        # for json_mapped_key, onto_mapped_to_value in self.mapping_elements.items():
        #     print("##  item to evaluate ##", json_mapped_key)
        #     if getJsonSchemaPropertieType(json_mapped_key) != "":
        #         results_for_mapped_entrance = evaluate_json_instances(data_to_evaluate, json_mapped_key, onto_mapped_to_value, ontology, jsonSchemaId)
        #         results_dicc[json_mapped_key] = results_for_mapped_entrance
        #     else :
        #         # ver como manejamos esto
        #         results_for_mapped_entrance = {}
            
        print("##---- Evaluation results: ", results_dicc, " ----##")
        return results_dicc
    

    # si todas las evaluaciones se van a basar en mapeos json esto se puede mover para la clase principal QualityMetric
    def get_data_to_evaluate(self) : 
        print("## SyntanticAccuracy: get_data_to_evaluate ##")
        storage_path = self.mapping_process.document_storage_path   
        JSONInstances = get_documents_from_storage(storage_path)

        print("## SyntanticAccuracy: Got json instances correctly ##")
        return JSONInstances
    
    async def save_result(self, result) -> None :     
        print("saved")

# this functions receives the attribute_path 'contacto-nombre' and builds the proper json key to find
# the value in the mapping document, adding the missing "rootObject", "key" and "type"
def build_mapping_entrance(attribute_field: FieldNode):
    #result = "rootObject-contacto-city_key#string"  
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

    def select_strategy(self, strategy: str) -> None:
        if strategy == SYNTCTATIC_ACCURACY:
            self._quality_strategy = SyntanticAccuracy()
            print("INSTANCIADA ")
    
    # antes: evaluate_quality(self, dq_model_id: str, request_mapping_body: Dict[str, Any])
    async def evaluate_quality(self, dq_model_id: str) -> None:
        # no se si vamos a menter esto o mandamos el mapping id como parametro siempre VER
        if dq_model_id != "":
           # ver si queda aca o lo mando por parametro al contstructor
           print("## Evaluacion 1.0 - about to se mapping process")
           await self.quality_strategy.set_mapping_process(dq_model_id)
           self.quality_strategy.set_dq_model_id(dq_model_id)
           print("## Evaluacion 2.0 - mapping process setted")
        # if request_mapping_body != {}:
        #     print("SETTING MAP ELEMENTS")
        #     self.quality_strategy.set_mapping_elements(request_mapping_body)
        result = await self._quality_strategy.evaluation()
        return result



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

# return evaluation result
# onto_values puede ser una lista si mapeo a mas de una cosa
# def evaluate_json_instances(json_instances, mapping_entrance, onto_mapped_to_value, ontology, jsonSchemaId) :
def evaluate_json_instances(json_instances, field_to_evaluate, mapping_entrance, onto_mapped_to_value, ontology, jsonSchemaId) :
    json_mapped_key = build_mapping_entrance(field_to_evaluate)
    # ver de donde sale mapping elements

    print("## Evaluacion 4.5.1 - onto mapped to", json_mapped_key, "###")
    print("## Evaluacion 4.5.2 - onto mapped to", len(json_instances))

    results_dicc = {}
    # algo temporal
    index = 1
    field_measures = []
    
    json_keys = find_json_keys(json_mapped_key)
    print("## Evaluacion 4.5.3 - json keys", json_keys)

    #metadata_repo.delete_existing_field_value_measures(json_keys, jsonSchemaId)
    
    # estas son las instancias de los jsons
    for json_instance in json_instances :
        print("## Evaluacion 4.5.4 - json keys", json_instance)
        # a partir de la entrada del mapping, busco el valor en el json
        result_key = json_mapped_key + "_" + str(index)
        # de mapping entrance podemos sacar el field
        # field = getfield(mapping_entrance)
        # destination
        print("## Evaluacion 4.5.5 - result key", result_key)
        index = index + 1
        
            
        # NODO_INSTANCIA = get_nodo_from_collection(json_instances.id)
        ## TODO: evaluar si obtener el nodo FIELD aca adentro!!!
        
        element = find_element_in_JSON_instance(json_instance, json_mapped_key)
        print("## Evaluacion 4.5.6 - found element", element)
        if element is None:
            value = 0
        # por cada ontología a la cual se haya mapeado
        # ver como guardar aca según la ongología a la que mapeo 
        # si esta OK en alguna de los ontologias se toma como que es válido
        for onto_mapped_to in onto_mapped_to_value:
            print("## Evaluacion 4.5.7 - onto value", onto_mapped_to['iri'])
            # ver aca si dejamos así o vemos la forma de modulizarlo
            onto_prop = getOntoPropertyByIri(onto_mapped_to['iri'], list(ontology.data_properties()))
            instances = list(onto_prop.get_relations())
            print("## Evaluacion 4.5.8 - onto instances", instances, " ##")
            ## instancias de las clases de la ontología
            for inst in instances:
                dp_value = inst[1]
                if(isinstance(dp_value, locstr)):
                    dp_value = str(dp_value)
                value = compare_onto_with_json_value(dp_value, element)
                print("## Evaluacion 4.5.8 - evaluation result", value, " ##")
                if value == 1:
                    break

        # setValorField(field, value)
        field_measures.append(value)

        #inserta los field value measures
        print("## Evaluacion 4.6 - insert value in neo4j", value, " ##")
        metadata_repo.insert_field_value_measures_v2(field_to_evaluate, value, json_instance['id'])
        results_dicc[result_key] = value

        
    #almacena un FieldMeasure por corrida, asi manetemos el historicos del las corridas
    # Aggregate all field measures and insert the result
    if field_measures:
        aggregated_measure_value = sum(field_measures) / len(field_measures)
        metadata_repo.insert_field_measures(json_keys, aggregated_measure_value, jsonSchemaId)

    # ver: pero de alguna forma devolver solo el resultado agregado
    return aggregated_measure_value

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

    # json_keys = ['contacto', 'city']
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

# find_json_keys gets the key of a mapping structure for example "contacto-city", and returns 
# a lis of the json keys of that entry: ['contacto','city'], this means that 'city' its an attribute inside 'contacto'
def find_json_keys_v2(path) :
    print(f'path ${path}') #contacto-city
    keys = path.split('-')
    return keys

def compare_onto_with_json_value(onto_prop_value, json_value) :
    # ver como hacer esto
    # queremos hacer esto?
    # hacer un toLower() aca o
    print("## Syntactic Accuracy: compare_onto_with_json_value onto:", onto_prop_value," json:", json_value,"##")
    if onto_prop_value == json_value:
        return 1
    return 0
  
# esta función compara un iri con un valor de un json
#Hotel" == "Hotel"
# "http://www.owl-ontologies.com/travel.owl#Hotel"
# "ruralarea"
# esto capaz se va
def compare_iri_with_json_value(iri, json_value) :
    # ver como hacer esto
    onto_name = iri.split('#')[1]
    print("iri name: ", onto_name)
    onto_name_lower = onto_name.lower()
    json_value.lower()

    return onto_name_lower == json_value
  