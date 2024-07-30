
VALUE = "value"
KEY = "key"

# ahora toma el mappingProcess por parámetro pero estaría guardado en una db
def process_mapping(mappingProcess):
    # guardar el proceso de mapeo en la base de datos (sea cual fuere)
    print("## Starting mapping process:", mappingProcess.ontology, "##")
    ontology = mappingProcess.ontology
    ontoClasses = ontology.classes()
    ontoObjectProperties = ontology.object_properties()
    ontoDataProperties = ontology.data_properties()

    mappedClasses = {}
    mappingItems = mappingProcess.mapping.items()
    for key, value in mappingProcess.mapping.items():
        print("processing key:", key)
        print("processing value:", value)
        # key: "destination_value", value: {"name" : "Destination", "iri"m "http://www.example.com/destination"}
        # en principio tomo como el mapeo es uno solo pero si es una lista seria recorer los elementos e ir aplicando la regla
        try :
            if isJSONValue(key):
                # Rule 1: an object is mapped to an ontology class
                mappedIris = validateRule1(key, value, ontoClasses)
                mappedClassKey = key.split("_")[0]
                mappedClasses[mappedClassKey] = mappedIris
                print("## Mapped OK ##", mappedClasses)             
            if isJSONKey(key):
                # Rule 2: a property is mapped to an ontology property   
                validateRule3(key, value, mappedClasses, ontoObjectProperties)
        except Exception as e:
            print("Error processing key:", key, "value:", value, "error:", e)
            raise e
    return None

# validateRule1 checks if the mappedTo iri is in the ontology classes
def validateRule1(key, mappedTo, ontoClasses):
    mappedIris = []
    for elem in mappedTo:
        print("Elem: ##", elem, "##")
        ontologyClassIri = elem['iri']
        if not isIriInOntologyElem(ontologyClassIri, ontoClasses):
            raise ValueError(f"Element {ontologyClassIri} not found in ontology classes")
        else :
            print("## Found ontology class:", elem['name'], "with iri:",ontologyClassIri, "##")
            mappedIris.append(ontologyClassIri)

    return mappedIris


# "destination-accomodation_key" : { name: "hasAccomodation", "iri": "http..."}
def validateRule3(key, value, mappedClasses, ontoObjectProperties):
    ontologyProperty = value["iri"]
    domainName = getParentProperty(key)
    rangeName =  getSonProperty(key)

    #
    domainIri = mappedClasses.get(domainName, None)
    # si no se mapeo, lo mapeamos nosotros a la clase que corresponda
    rangeIri = mappedClasses.get(rangeName, None)
    # se asumen mapeadas las clases de dominio y rango, creo que nuestra precondición iba hasta el dominio no mas
    # quizas se puede asumir que si el usuario hizo este mapeo a object properties, nosotros asignamos el mapeo
    # al rango (no recuerdo si lo definimos así o no lo pensamos)
    if domainIri is None:
        return False
    
    objectProperty = getObjectPropertyByIri(ontologyProperty, ontoObjectProperties)
    if objectProperty is None:
        return False
    
    isDomainOk = isIriInOntologyElem(domainIri, objectProperty.domain)
    isRangeOk = isIriInOntologyElem(rangeIri, objectProperty.range)

    return isDomainOk and isRangeOk

def isIriInOntologyElem(iri, ontoElems):
    for elem in ontoElems    :
        if elem.iri == iri:
            return True

    return False

def getObjectPropertyByIri(iri, ontoObjectProperties):
    for obj_prop in ontoObjectProperties:
        if obj_prop.iri == iri:
            return obj_prop

    return None

# getParentProperty gets the parent property of a json key, its splits de key by "-"" and gets the penultimate element
# the final element is the property being manipulated, the penultimate will be the parent of that property
def getParentProperty(jsonKey):
    # en principio se deja como padre toda la cadena que esta antes del ultimo elemento
    # es decir el padre de "destination-accomodation-ratings_key" es "destination-accomodation"
    # ya que puede haber otro elemento del json con un campo accomodation pero esta anidado en otra parte 
    jsonKeys = jsonKey.rsplit("-",1)
    parent = jsonKeys[0]
    return parent

def getSonProperty(jsonKey):
    son = jsonKey.split("_")[0]
    # se deja como hijo toda la cadena, por si hay elementos repetidos
    # es decir de "destination-accomodation-ratings_key" el hijo es "destination-accomodation-ratings"
    return son

def isJSONValue(str):
    defPart = str.split("_")
    return defPart[1] == VALUE

def isJSONKey(str):
    defPart = str.split("_")
    return defPart[1] == KEY