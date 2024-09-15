from app.database import mapping_process_collection, onto_collection
from bson import ObjectId
from app.domain.mapping.models import MappingProcess, MappingProcessDocument,OntologyDocument
from app.domain.dataquality.mocks import get_hardcoded_test_documents
from app.domain.mapping.service import getOntoPropertyByIri, getJsonSchemaPropertieType
from owlready2 import get_ontology
from typing import Dict, Any
from typing import Dict, Any
from abc import ABC, abstractmethod

SYNTCTATIC_ACCURACY = "syntactic_accuracy"
QUALITY_RULES = [SYNTCTATIC_ACCURACY]

class QualityMetric(ABC) : 
    async def evaluation(self) -> None :
        print("## QualityMetric: evaluation ##")
        data = self.get_data_to_evaluate()
        print("## QualityMetric: data ##", data)
        result = await self.execute_measure(data)
        await self.save_result(result) # esto capaz se mueve para execute_measure y se guarda enseguida que se calcula

    @abstractmethod
    def get_data_to_evaluate(self) -> None : 
        pass

    @abstractmethod  
    async def execute_measure(self, data) :    
        pass
    
    @abstractmethod
    async def save_result(self, result) -> None :     
        pass

    async def set_mapping_process(self, mapping_process_id: str) -> None:
        pass

    def set_mapping_elements(self, mapping_elems:  Dict[str, Any]) -> None:
        pass

class SyntanticAccuracy(QualityMetric) :
    def __init__(self) -> None:
        self.mapping_process_id: str = ""
        self.mapping_process: MappingProcessDocument = None
        self.mapping_elements:  Dict[str, Any] = {}
        pass
    
    async def set_mapping_process(self, mapping_process_id: str) -> None:
        print("## Iniciating SyntaticAccuracy with mp id : ", mapping_process_id + " ##")
        mapping_process = await get_mapping_process(mapping_process_id)
        self.mapping_process = mapping_process
    
    def set_mapping_elements(self, mapping_elems:  Dict[str, Any]) -> None:
        print("## SyntanticAccuracy: set_mapping_elements ##", mapping_elems)
        self.mapping_elements = mapping_elems

    async def execute_measure(self, data_to_evaluate) :
        # ver ss movemos esto
        print("## SyntanticAccuracy: execute_measure ##")
        ontology = await get_onto(self.mapping_process.ontologyId)
        print("## Got ontology correctly ##", list(ontology.individuals()))
        print("## SyntanticAccuracy: mapping elements ##") #self.mapping_elements)
        for json_mapped_key, onto_mapped_to_value in self.mapping_elements.items():
            print("##  item to evaluate ##", json_mapped_key)
            if getJsonSchemaPropertieType(json_mapped_key) != "":
                evaluate_json_instances(data_to_evaluate, json_mapped_key, onto_mapped_to_value, ontology)
        return None
    
    # si todas las evaluaciones se van a basar en mapeos json esto se puede mover para la clase principal QualityMetric
    def get_data_to_evaluate(self) : 
        print("## SyntanticAccuracy: get_data_to_evaluate ##")
        storage_path = self.mapping_process.document_storage_path   
        JSONInstances = get_documents_from_storage(storage_path)

        print("## SyntanticAccuracy: Got json instances correctly ##")
        return JSONInstances
    
    async def save_result(self, result) -> None :     
        print("saved")
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
        
    async def evaluate_quality(self, mapping_id: str, request_mapping_body: Dict[str, Any]) -> None:
        # no se si vamos a mentere esto o mandamos el mapping id como parametro siempre VER
        if mapping_id != "":
           # ver si queda aca o lo mando por parametro al contstructor
           await self.quality_strategy.set_mapping_process(mapping_id)
        if request_mapping_body != {}:
            print("SETTING MAP ELEMENTS")
            self.quality_strategy.set_mapping_elements(request_mapping_body)
            

        result = await self._quality_strategy.evaluation()


async def get_mapping_process(mapping_processID: str) -> MappingProcessDocument:
    mapping_processID = ObjectId(mapping_processID)
    mapping_process_document = await mapping_process_collection.find_one({'_id': mapping_processID})
    mapping_process_docu = MappingProcessDocument(**mapping_process_document)
    
    return mapping_process_docu

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
    data = get_hardcoded_test_documents()
    return data

# return evaluation result
# onto_values puede ser una lista si mapeo a mas de una cosa
def evaluate_json_instances(json_instances, mapping_entrance, onto_values, ontology) :
    print("## evaluate_json_instances ##", json_instances)
    for json_instance in json_instances :
        # a partir de la entrada del mapping, busco el valor en el json
        element = find_element_in_JSON_instance(json_instance, mapping_entrance)
        print("elemento found: ", element)
        if element is None:
            # aca enteindo se guardaría el valor de la evaluación en los metadatos => 0 en este caso
            value =  0
            print(" Evaluation for ", element, " is ", value)
        # por cada ontología a la cual se haya mapeado
        for onto_value in onto_values :
            # estoy evaluando un json value en este caso!
            # busco la clase de la ontologia a la cual se mapeo y recorro sus instancias
            print("Onto value: ", onto_value['iri'])
            # ver aca si dejo así o vemos la forma de modulizarlo
            onto_class = getOntoPropertyByIri(onto_value['iri'], list(ontology.data_properties()))
            print("onto class: ", onto_class)
            instances = list(onto_class.individuals())
            print("HERE")
            print("onto instances: ", instances)
            for inst in instances:
                print("onto instance: ", inst)
                result = compare_iri_with_json_value(onto_value['iri'], element)
                print("result of comparison: ", result)

# esta función busca un elemento en un json a partir de un path dado por la entrada del mapping
# destination-accomodation-name
# accomodation aca puedo recibir value
def find_element_in_JSON_instance(json_document, path) :
    keys = path.replace('-', '_').split('_')
    json_keys = keys[:-1]
    print("keys", json_keys)
    # jsonFlated := [destination.accomation.name = Paris, kfkfkfkfk]
    # jsonFlated[destination.accomation.name] = Paris
    #
    element = json_document
    try:
        for key in json_keys:
            print("## key: ", key)
            print("## element: ", element)
            element = element[key]
        print("About to return element: ", element)
        return element
    except (KeyError, TypeError):
        return None

# esta función compara un iri con un valor de un json
#Hotel" == "Hotel"
# "http://www.owl-ontologies.com/travel.owl#Hotel"
# "ruralarea"
def compare_iri_with_json_value(iri, json_value) :
    # ver como hacer esto
    onto_name = iri.split('#')[1]
    print("iri name: ", onto_name)
    onto_name_lower = onto_name.lower()
    json_value.lower()

    return onto_name_lower == json_value
  