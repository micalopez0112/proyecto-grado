
VALUE = "value"
KEY = "key"

# ahora toma el mappingProcess por parámetro pero estaría guardado en una db
def process_mapping(mappingProcess):
    # guardar el proceso de mapeo en la base de datos (sea cual fuere)
    print("## Starting mapping process:", mappingProcess.ontology, "##")
    ontology = mappingProcess.ontology
    ontoClasses = list(ontology.classes())
    ontoObjectProperties = ontology.object_properties()
    ontoDataProperties = ontology.data_properties()

    mappedClasses = {}
    newMappedClasses = {}
    mappingItems = mappingProcess.mapping.items()
    for jsonMappedKey, ontoValue in mappingProcess.mapping.items():
        print("processing key:", jsonMappedKey)
        print("processing value:", ontoValue)
        okRule3 = False
        okRule2 = False
        # key: "destination_value", value: {"name" : "Destination", "iri"m "http://www.example.com/destination"}
        # en principio tomo como el mapeo es uno solo pero si es una lista seria recorer los elementos e ir aplicando la regla
        try :
            if isJSONValue(jsonMappedKey):
                # Rule 1: an object is mapped to an ontology class
                print("Sending onto clases with len: ",len(ontoClasses))
                mappedIris = validateRule1(jsonMappedKey, ontoValue, ontoClasses)
                mappedClassKey = jsonMappedKey.split("_")[0]
                mappedClasses[mappedClassKey] = mappedIris
                print("## Mapped OK ##", mappedClasses)             
            if isJSONKey(jsonMappedKey):
                # Rule 2: a property is mapped to an ontology property   
                okRule3, possibleErrors = validateRule3(jsonMappedKey, ontoValue, mappedClasses, ontoObjectProperties, newMappedClasses)
                if okRule3:
                    continue
           
                okRule2, possibleRule2Errors = validateRule2(jsonMappedKey, ontoValue, mappedClasses, ontoDataProperties)
                if not okRule2:
                    possibleErrors.extend(possibleRule2Errors)
                    raise ValueError(f"Errors found: {possibleErrors}")
        except Exception as e:
            print("ERROR processing key:", jsonMappedKey, "value:", ontoValue, "error:", e)
            raise e
    
    originalMappingJson = mappingProcess.mapping
    for key, value in newMappedClasses.items():
        if key in originalMappingJson:
            originalMappingJson[key].extend(value)
        else:
            originalMappingJson[key] = value
    print("## Final mapping: ", originalMappingJson, "##")
    return None

# Aparentemente esta validación estaría funcionando ok
# validateRule1 checks if the mappedTo iri is in the ontology classes and append the mapped class Iri to the mappedClasses dict
def validateRule1(key, ontoValuesMappedTo, ontoClasses):
    mappedIris = []
    for ontoElem in ontoValuesMappedTo:
        print("Elem: ##", ontoElem, "##")
        ontologyClassIri = ontoElem['iri']
        if not isIriInOntologyElem(ontologyClassIri, ontoClasses):
            raise ValueError(f"Element {ontologyClassIri} not found in ontology classes")
        else :
            print("## Found ontology class:", ontoElem['name'], "with iri: ",ontologyClassIri, "##")
            mappedIris.append(ontologyClassIri)

    return mappedIris


# validateRule3 recieves the json-schema key, the ontology values mapped to and all valid ontolgy object properties. Then it does the next validations: 
# 1. checks if the ontology value is an existent objet property 
# 2. checks if the domain of the object property is already correctly mapped (by checking if it is in the mappedClasses dict)
# 3. checks if the range of the object property is already correctly mapped. If it isn't it maps it to the correct class and adds it to the newMappedClasses
# then at the end of all mapping iteration it adds the new mapped elements to the mapping json.
def validateRule3(key, ontoValuesMappedTo, mappedClasses, ontoObjectProperties, newMappedClasses):
    possibleErrors = []
    print("### Validating rule 3: ", key, "##", ontoValuesMappedTo, "###")
    for ontoElem in ontoValuesMappedTo:
        isDomainOk = False
        isRangeOk = False
        ontologyProperty = ontoElem["iri"]
        domainName = getParentProperty(key)
        rangeName =  getSonProperty(key)

        print("## DomainName:", domainName, "##")
        print("## RangeName:", rangeName, "##")
        # ojo porque esto es una lista! (ya que una property del json puede haber sido mapeado a varias clases)
        domainIrisList = mappedClasses.get(domainName, None)
        rangeIrisList = mappedClasses.get(rangeName, None)
        if domainIrisList is None:
            raise ValueError(f"Element name:{domainName} Iiri:{domainIrisList} not mapped to a class")
        
        objectProperty = getOntoPropertyByIri(ontologyProperty, ontoObjectProperties)
        if objectProperty is None:
            possibleErrors.append(f"Element {ontologyProperty} not found in ontology object properties")
            return False, possibleErrors
        
        for domainIri in domainIrisList:
            isDomainOk = isIriInOntologyElem(domainIri, objectProperty.domain)
            if isDomainOk:
                break

        if not isDomainOk:
            possibleErrors.append(f"Element {domainIri} not found in object property domain")
            return False, possibleErrors
        
        if rangeIrisList is None:
            print("## RangeIri is None, mapeamos al primer elemento del rango ##")
            # TODO: Hay un tema acá el rango puede ser varios elementos, en ese caso que hacemos? 
            # de momento mapeo al primer
            # si no se mapeo, lo mapeamos nosotros a la clase que corresponda
            rangeClass = objectProperty.range[0]
            classKey = rangeName + "_value"
            if classKey in newMappedClasses:
                newMappedClasses[classKey].append({"name": rangeClass.name, "iri": rangeClass.iri})
            else:
                newMappedClasses[classKey] = [{"name": rangeClass.name, "iri": rangeClass.iri}]
            isRangeOk = True
        else: 
            for rangeIri in rangeIrisList:
                isRangeOk = isIriInOntologyElem(rangeIri, objectProperty.range)
                if isRangeOk:
                    break
    
            if not isRangeOk:
                possibleErrors.append(f"Element {rangeIri} not found in object property range")
                return False, possibleErrors

    return isDomainOk and isRangeOk, possibleErrors

# validateRule2 recieves the json-schema key, the ontology values mapped to and all valid ontolgy data properties. Then it does the next validations:
# 1. checks if the ontology value is an existent data property
# 2. checks if the domain of the data property is already correctly mapped (by checking if it is in the mappedClasses dict)
def validateRule2(key, mappedTo, mappedClasses, ontoDataProperties):
    print("### Validating rule 2: ", key, "##", mappedTo, "###")
    possibleErrors = []
    for ontoElem in mappedTo:
        ontologyPropertyIri = ontoElem["iri"]
        print("## Ontology property iri: ", ontologyPropertyIri, "##")
        domainName = getParentProperty(key)
        rangeName =  getSonProperty(key)

        domainIrisList = mappedClasses.get(domainName, None)
        if domainIrisList is None:
            raise ValueError(f"Element {domainIrisList} not mapped to a class")
        
        dataProperty = getOntoPropertyByIri(ontologyPropertyIri, ontoDataProperties)
        if dataProperty is None:
            possibleErrors.append(f"Element {ontologyPropertyIri} not found in ontology data properties")
            return False, possibleErrors

        for domainIri in domainIrisList:
            isDomainOk = isIriInOntologyElem(domainIri, dataProperty.domain)
            if isDomainOk:
                break
    
        if not isDomainOk:
            possibleErrors.append(f"Element {domainIri} not found in data property domain")
            return False, possibleErrors
        # Tengo que de alguna forma validar que el tipo del rango es el mismo que el de la property del json
    return True, possibleErrors
        
# isIriInOntologyElem checks if an iri exists in an ontology elements list (class, property, etc)
def isIriInOntologyElem(iri, ontoElems):
    for elem in ontoElems:
        if elem.iri == iri:
            return True

    return False

def getOntoPropertyByIri(iri, ontoProperties):
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
    print("## Parent property: ", parent, "##")
    return parent

def getSonProperty(jsonKey):
    son = jsonKey.split("_")[0]
    # se deja como hijo toda la cadena, por si hay elementos repetidos
    # es decir de "destination-accomodation-ratings_key" el hijo es "destination-accomodation-ratings"
    print("## Son property: ", son, "##")
    return son

def isJSONValue(str):
    defPart = str.split("_")
    return defPart[1] == VALUE

def isJSONKey(str):
    defPart = str.split("_")
    return defPart[1] == KEY