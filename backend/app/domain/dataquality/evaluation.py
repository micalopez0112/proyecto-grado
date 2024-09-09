from app.database import mapping_process_collection, onto_collection
from bson import ObjectId
from app.domain.mapping.models import MappingProcess, MappingProcessDocument,OntologyDocument
from app.domain.dataquality.mocks import get_hardcoded_test_documents
from app.domain.mapping.service import isJSONValue, getOntoPropertyByIri
from owlready2 import get_ontology
# this function will access the storage and get the documents
# we need to define the storage service or how we will access it
def get_documents_from_storage(path : str) :
    data = get_hardcoded_test_documents()
    return data

# this function will evaluate the data quality of the documents
# que vamos a recibir aca? en principio se asume que viene el pedazo de mapping que quiero evaluar
# de momento recibo el mapping_processID
# ver como vamos a saber a donde ir a buscar las instacias
async def evaluate_data_quality(instances_path: str, mapping_processID : str) :
    # get documents from storage
    mapping_processID = ObjectId(mapping_processID)
    mapping_process_document = await mapping_process_collection.find_one({'_id': mapping_processID})
    mapping_process_docu = MappingProcessDocument(**mapping_process_document)
    # obtengo la ontología
    onto_id = ObjectId(mapping_process_docu.ontologyId)
    ontology_docu = await onto_collection.find_one({'_id': onto_id})
    ontology_document = OntologyDocument(**ontology_docu)
    ontology_path = ontology_document.uri
    if ontology_document.type == "FILE":
        ontology_path = ontology_document.file
    ontology = get_ontology(ontology_path).load()

    # para cada instancia del json evaluo la calidad de los datos
    mapping = mapping_process_docu.mapping
    JSONInstances = get_documents_from_storage(instances_path)
    print("### got json instances ###")
    for json_mapped_key, onto_value in mapping.items():
        print("##  item to evaluate ##", json_mapped_key)
        if isJSONValue(json_mapped_key) :
            print("is JSON value")
            evaluate_json_instances(JSONInstances, json_mapped_key, onto_value, ontology)
    #

# return evaluation result
# onto_values puede ser una lista si mapeo a mas de una cosa
def evaluate_json_instances(json_instances, mapping_entrance, onto_values, ontology) :
    for json_instance in json_instances :
        # si no existe retorno 0
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
            onto_class = getOntoPropertyByIri(onto_value['iri'], list(ontology.classes()))
            print("onto class: ", onto_class)
            instances = list(onto_class.individuals())
            print("HERE")
            print("onto instances: ", instances)
            for inst in instances:
                print("onto instance: ", inst)
                result = compare_iri_with_json_value(onto_value['iri'], element)
                print("result of comparison: ", result)


# esta función busca un elemento en un json a partir de un path dado por la entrada del mapping
def find_element_in_JSON_instance(json_document, path) :
    keys = path.replace('-', '_').split('_')
    json_keys = keys[:-1]
    print("keys", json_keys)
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
def compare_iri_with_json_value(iri, json_value) :
    # ver como hacer esto
    onto_name = iri.split('#')[1]
    print("iri name: ", onto_name)
    onto_name_lower = onto_name.lower()
    json_value.lower()

    return onto_name_lower == json_value
  