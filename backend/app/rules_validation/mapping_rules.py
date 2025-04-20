from app.models.schema import JsonSchema
from owlready2 import Thing, ThingClass, ObjectProperty, DataProperty

VALUE = "value"
KEY = "key"

mapping_type_separator='?'

simpleTypes = ["string", "integer", "bool", "number"]

def validate_mapping(mapping, ontology, jsonschema: JsonSchema):
    """Validate mapping between JSON schema and ontology.
    
    Args:
        mapping: Dictionary with mapping rules
        ontology: Ontology object containing classes and properties
        jsonschema: JSON schema to validate against
        
    Raises:
        ValueError: If validation fails with list of errors
    """
    onto_classes=list(ontology.classes())
    onto_object_props=list(ontology.object_properties())
    onto_data_props=list(ontology.data_properties())
    alreadyMappedClasses = {}
    mapping_items = mapping.items()

    # Sort mappings to process classes first
    mapping_items_sorted = sorted(mapping_items, key=lambda x: isJSONValue(x[0]), reverse=True)
    possibleErrors = []
    for jsonMappedKey, ontoValue in mapping_items_sorted:
        okRule3 = False
        okRule2 = False
        # en principio tomo como el mapeo es uno solo pero si es una lista seria recorer los elementos e ir aplicando la regla
        try :
            if isJSONValue(jsonMappedKey):
                # Rule 1: an object is mapped to an ontology class
                mappedIris = validate_class_mapping(ontoValue, onto_classes)
                mappedClassKey = jsonMappedKey.split(mapping_type_separator)[0]
                alreadyMappedClasses[mappedClassKey] = mappedIris
            if isJSONKey(jsonMappedKey):              
                # Rule 2: a simple property is mapped to an ontology data property
                JSPropertyType = get_json_schema_property_type(jsonMappedKey)
                if JSPropertyType != "" and (JSPropertyType in simpleTypes):
                    okRule2, possibleRule2Errors = validate_data_property_mapping(jsonMappedKey, ontoValue, alreadyMappedClasses, onto_data_props, JSPropertyType, None, onto_classes)
                    if not okRule2:
                        possibleErrors.extend(possibleRule2Errors)
                        raise ValueError(f"Possible errors: {possibleErrors}")
                elif JSPropertyType != "" and (JSPropertyType == "array"):
                    posibleArrayErrors = []
                    if is_mapping_to_OP(ontoValue, onto_object_props):
                        okRule3, posibleArrayErrors = validate_object_property_mapping(jsonMappedKey, ontoValue, alreadyMappedClasses, onto_object_props, JSPropertyType,jsonschema, onto_classes) 
                    else :
                        okRule2, posibleArrayErrors = validate_data_property_mapping(jsonMappedKey, ontoValue, alreadyMappedClasses, onto_data_props, JSPropertyType, jsonschema, onto_classes)
                    
                    if okRule2 or okRule3:
                        continue
                    
                    raise ValueError(f"Possible errors: {posibleArrayErrors}")
                else:
                    # Rule 3: an object property is mapped to an ontology property   
                    okRule3, possibleErrors = validate_object_property_mapping(jsonMappedKey, ontoValue, alreadyMappedClasses, onto_object_props, "",None, onto_classes)
                    if okRule3:
                        continue
                    else:
                        raise ValueError(f"Possible errors: {possibleErrors}")
        except Exception as e:
            print("ERROR processing key:", jsonMappedKey, "value:", ontoValue, "error:", e)
            raise e
    
    originalMappingJson = mapping
    return None


# validate_class_mapping checks if the mappedTo iri is in the ontology classes and append the mapped class Iri to the alreadyMappedClasses dict
def validate_class_mapping(onto_values_mapped_to, onto_classes):
    print("## Validating rule 1: ##")
    mapped_iris = []
    for onto_elem in onto_values_mapped_to:
        ontologyClassIri = onto_elem['iri']
        if not isIriInOntologyElem(ontologyClassIri, onto_classes):
            raise ValueError(f"Element {ontologyClassIri} not found in ontology classes")
        else :
            print("## Found ontology class:", onto_elem['name'], "with iri: ",ontologyClassIri, "##")
            mapped_iris.append(ontologyClassIri)

    return mapped_iris

# is_mapping_to_OP checks if the the first mapped iri is an object property
def is_mapping_to_OP(ontoValuesMappedTo, ontoObjectProperties):
    ontoValues = list(ontoValuesMappedTo)
    firstMappedIri = ontoValues[0]['iri']
    if isIriInOntologyElem(firstMappedIri, ontoObjectProperties):
        return True
    else :
       return  False


# validate_object_property_mapping recieves the json-schema key, the ontology values mapped to and all valid ontolgy object properties. Then it does the next validations: 
# 1. checks if the ontology value is an existent objet property 
# 2. checks if the domain of the object property is already correctly mapped (by checking if it is in the alreadyMappedClasses dict)
# 3. checks if the range of the object property is already correctly mapped. If it isn't it maps it to the correct class and adds it to the newalreadyMappedClasses
# then at the end of all mapping iteration it adds the new mapped elements to the mapping json.
def validate_object_property_mapping(json_mapped_key, ontoValuesMappedTo, alreadyMappedClasses, ontoObjectProperties, JSONPropertyType, jsonschema: JsonSchema, ontoClasses):
    possibleErrors = []
    print("### Validating rule 3: ", json_mapped_key, "##", ontoValuesMappedTo, "###")
    domainName = getParentProperty(json_mapped_key)
    rangeName =  getSonProperty(json_mapped_key)
    domainIrisList = alreadyMappedClasses.get(domainName, None)     
    rangeIrisList = alreadyMappedClasses.get(rangeName, None)
    for ontoElem in ontoValuesMappedTo:
        isDomainOk = False
        isRangeOk = False
        ontologyProperty = ontoElem["iri"]
        # ojo porque esto es una lista! (ya que una property del json puede haber sido mapeado a varias clases)
        if domainIrisList is None:
            possibleErrors.append(f"Element name:{domainName} I not mapped to a class")
            return False, possibleErrors
        
        if rangeIrisList is None:
            possibleErrors.append(f"Element name:{rangeName} not mapped to a class")
            return False, possibleErrors

        objectProperty = getOntoPropertyByIri(ontologyProperty, ontoObjectProperties)
        if objectProperty is None:
            possibleErrors.append(f"Element {ontologyProperty} not found in ontology object properties")
            return False, possibleErrors
        
        for domainIri in domainIrisList:
            isDomainOk = isIriInOntologyElem(domainIri, objectProperty.domain)
            if isDomainOk:
                break

        if not isDomainOk:
            possibleErrors.append(f"Element {domainIri} not found in object property {objectProperty.name} domain")
            return False, possibleErrors
        
        if JSONPropertyType == "array":
            propType = "object"
            is_ok = check_all_json_schema_types(jsonschema, json_mapped_key, propType)
            if not is_ok:
                possibleErrors.append(f"If you're mapping {json_mapped_key} to a objectProperty all the types of the array must be objects")
                return False, possibleErrors

        for rangeIri in rangeIrisList:
            isRangeOk = isIriInOntologyElem(rangeIri, objectProperty.range)
            if isRangeOk:
                # si alguna de las clases del rango esta mapeada ya estoy OK
                break
    
        # si no se encontró el rango en el ontolgy range, se busca entre los ancestros, ya que se heredan las propiedades al  ser subclase
        if not isRangeOk:
            rangeMappedClass = getOntoPropertyByIri(rangeIri, ontoClasses)
            isRangeAnAncestor = check_class_ancestors(rangeMappedClass, objectProperty.range)
            if isRangeAnAncestor:
                isRangeOk = True
            if not isRangeAnAncestor:
                possibleErrors.append(f"Element {rangeIri} not found in object property range")
                return False, possibleErrors

    return isDomainOk and isRangeOk, possibleErrors

# validate_data_property_mapping recieves the json-schema key, the ontology values mapped to and all valid ontolgy data properties. Then it does the next validations:
# 1. checks if the ontology value is an existent data property
# 2. checks if the domain of the data property is already correctly mapped (by checking if it is in the alreadyMappedClasses dict)
def validate_data_property_mapping(json_mapped_key, ontoValuesMappedTo, alreadyMappedClasses, ontoDataProperties, JSONPropertyType, jsonschema: JsonSchema, ontoClasses):
    print("### Validating rule 2: ", json_mapped_key, "##", ontoValuesMappedTo, "###")
    possibleErrors = []
    isRangeOk = True
    domainName = getParentProperty(json_mapped_key)
    domainIrisList = alreadyMappedClasses.get(domainName, None)
    if domainIrisList is None:
        possibleErrors.append(f"Element {domainIrisList} not mapped to a class")
        return False, possibleErrors

    for ontoElem in ontoValuesMappedTo:
        ontologyPropertyIri = ontoElem["iri"]
        data_property = getOntoPropertyByIri(ontologyPropertyIri, ontoDataProperties)
        if data_property is None:
            possibleErrors.append(f"Element {ontologyPropertyIri} not found in ontology data properties")
            return False, possibleErrors

        # se verifica que el domain de la dp esté correctamente mapeado a una clase
        # para ello se recorre la lista de iris mapeados al domain
        for domainIri in domainIrisList:
            domainMappedClass = getOntoPropertyByIri(domainIri, ontoClasses)
            isDomainOk = isIriInOntologyElem(domainIri, data_property.domain)         
            if isDomainOk:
                break
        
        # si no se encontró el domain en el ontolgy domain, se busca entre los ancestros, ya que se heredan las propiedades al  ser subclase
        if not isDomainOk:
            is_domain_an_ancestor = check_class_ancestors(domainMappedClass, data_property.domain)
            if not is_domain_an_ancestor:
                possibleErrors.append(f"Element {domainIri} is not an ancestor of {data_property.domain}")
                return False, possibleErrors
            
        if not isDomainOk and not is_domain_an_ancestor:
            possibleErrors.append(f"Element {domainIri} not found in data property domain")
            return False, possibleErrors
        
        # si estoy validando un mapeo de array a dp tiene que cumplir que todos sus tipos son simples
        if JSONPropertyType == "array":
            prop_type = "simple"
            isOk = check_all_json_schema_types(jsonschema, json_mapped_key, prop_type)
            if not isOk:
                possibleErrors.append(f"If you're mapping {json_mapped_key} to a dataproperty, all the types of the array must be simple")
                return False, possibleErrors
        
    return isRangeOk, possibleErrors


# check_class_ancestors checks if a class is an ancestor of another class. This is needed when checking if a class is a subClass of another class
def check_class_ancestors(domainMappedClass, wantedAncestorClasses):
    for wantedAncestorClass in wantedAncestorClasses:
        for ancestor in domainMappedClass.ancestors():
            if ancestor.iri == wantedAncestorClass.iri:
                return True
    return False


def check_all_json_schema_types( jsonSchema: JsonSchema, key, propType):
    jsonSchema = JsonSchema(**jsonSchema)
    propertyBeingLooked = jsonSchema.findPropertyInJsonSchema(key)
    if propertyBeingLooked is None:
        return False

    if propertyBeingLooked["type"] != "array":
        return False

    items = propertyBeingLooked["items"]
    if propType == "simple" and items["type"] not in simpleTypes:
            return False
    if propType == "object" and items["type"] != "object":
        return False
        
    print("## All properties are##", propType)    
    return True


# isIriInOntologyElem checks if an iri exists in an ontology elements list (class, property, etc)
def isIriInOntologyElem(iri, ontoElems):
    ontoElemsCopy = ontoElems
    for elem in ontoElemsCopy:
        if elem.iri == iri:
            return True

    return False

def getOntoPropertyByIri(iri, ontoProperties):
    # se copia en una variable, porque si no se modifica el original
    for obj_prop in ontoProperties:
        if obj_prop.iri == iri:
            return obj_prop

    return None

# getParentProperty gets the parent property of a json key, its splits de key by "-"" and gets the penultimate element
# the final element is the property being manipulated, the penultimate will be the parent of that property
def getParentProperty(jsonKey):
    # en principio se deja como padre toda la cadena que esta antes del ultimo elemento
    # es decir el padre de "destination-accomodation-ratings_key" es "destination-accomodation"
    # ya que puede haber otro elemento del json con un campo accomodation pero esta anidado en otra parte 
    # rsplit me splitea el último - y me deja el resto de la cadena
    jsonKeys = jsonKey.rsplit("-",1)
    parent = jsonKeys[0]
    return parent

def getSonProperty(jsonKey):
    son = jsonKey.split(mapping_type_separator)[0]
    # se deja como hijo toda la cadena, por si hay elementos repetidos
    # es decir de "destination-accomodation-ratings_key" el hijo es "destination-accomodation-ratings"
    return son

def isJSONValue(str):
    splittedMappingKey = str.split(mapping_type_separator)
    return splittedMappingKey[1] == VALUE

def isJSONKey(str):
    splittedMappingKey = str.split(mapping_type_separator)
    # if the mapping was done to a data property concatenated with a "-" next to the key comes the property type: 
    # example: "accomodation-ratings_key-string"
    keyPart = splittedMappingKey[1].split("#")
    return keyPart[0] == KEY

# get_json_schema_property_type returns the property type (string, int, bool, float, array) of a json property
def get_json_schema_property_type(str):
    splittedMappingKey = str.split(mapping_type_separator)
    keyPart = splittedMappingKey[1]
    hashTag = keyPart.split("#")
    if len(hashTag) > 1:
        return hashTag[1]
    return ""

# mover para otro file pero dentro de este mismo modulo
# find_json_keys gets the key of a mapping structure for example "#contacto-city_key#string", and returns 
# a lis of the json keys of that entry: ['contacto','city'], this means that 'city' its an attribute inside 'contacto'
def find_json_keys(path) :
    print(f'path ${path}') #contacto-city?key#string
    keys = path.replace('-', mapping_type_separator).split(mapping_type_separator)

    json_keys = keys[:-1] 
    json_keys.remove('rootObject')
    return json_keys

# esta función busca un elemento en un json a partir de un path dado por la entrada del mapping
# destination-accomodation-name
# accomodation aca puedo recibir value
# TODO: ver posibilidad de obtener el nodo FIELD, aprovechando la anidación entre los campos del json
def find_element_in_JSON_instance(json_document, path) :
    keys = path.replace('-', mapping_type_separator).split(mapping_type_separator)

    json_keys = keys[:-1] 
    json_keys.remove('rootObject')
    element = json_document
    try:
        for key in json_keys:
            element = element[key]
        return element
    except (KeyError, TypeError):
        return None