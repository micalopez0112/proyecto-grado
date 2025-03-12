from app.models.schema import JsonSchema

VALUE = "value"
KEY = "key"
# constantes
mapping_type_separator='?'

simpleTypes = ["string", "integer", "bool", "number"]
# TODO: revisar el tema del orden, mirar la tesis de aquellos para ver como hacian, ahora como esta hecho 
# se asume que todos los mapeos de clases vienen primero.!!
# ahora toma el mappingProcess por parámetro pero estaría guardado en una db
# ojo ver si este tipado funciona
def validate_mapping(mapping, ontology, jsonschema: JsonSchema):
    # guardar el proceso de mapeo en la base de datos (sea cual fuere)
    print("## Starting mapping process:", ontology, "##")
    ontoClasses = list(ontology.classes())
    ontoObjectProperties = ontology.object_properties()
    ontoDataProperties = ontology.data_properties()

    mappedClasses = {}
    newMappedClasses = {}
    mappingItems = mapping.items()
    mappignItemsOrdered = sorted(mappingItems, key=lambda x: isJSONValue(x[0]), reverse=True)
    # Ordenamos los mapeos de clases primero
    possibleErrors = []
    ontoObjectPropertiesList = list(ontoObjectProperties)
    ontoDataPropertiesList = list(ontoDataProperties)
    for jsonMappedKey, ontoValue in mappignItemsOrdered:
        okRule3 = False
        okRule2 = False
        print("## Processing key:", jsonMappedKey, "value:", ontoValue, "##")
        # en principio tomo como el mapeo es uno solo pero si es una lista seria recorer los elementos e ir aplicando la regla
        try :
            if isJSONValue(jsonMappedKey):
                # Rule 1: an object is mapped to an ontology class
                mappedIris = validateRule1(jsonMappedKey, ontoValue, ontoClasses)
                mappedClassKey = jsonMappedKey.split(mapping_type_separator)[0]
                mappedClasses[mappedClassKey] = mappedIris
                print("## Mapped OK ##", mappedClasses)             
            if isJSONKey(jsonMappedKey):              
                # Rule 2: a simple property is mapped to an ontology data property
                JSPropertyType = getJsonSchemaPropertieType(jsonMappedKey)
                if JSPropertyType != "" and (JSPropertyType in simpleTypes):
                    print("is data property mapping")
                    okRule2, possibleRule2Errors = validateRule2And4(jsonMappedKey, ontoValue, mappedClasses, ontoDataPropertiesList, JSPropertyType, None, ontoClasses)
                    if not okRule2:
                        possibleErrors.extend(possibleRule2Errors)
                        raise ValueError(f"Possible errors: {possibleErrors}")
                elif JSPropertyType != "" and (JSPropertyType == "array"):
                    posibleArrayErrors = []
                    # acomodar
                    if IsMappedToOP(ontoValue, ontoObjectPropertiesList):
                        okRule3, posibleArrayErrors = validateRule3And4(jsonMappedKey, ontoValue, mappedClasses, ontoObjectPropertiesList, JSPropertyType,jsonschema, ontoClasses) 
                    else :
                        okRule2, posibleArrayErrors = validateRule2And4(jsonMappedKey, ontoValue, mappedClasses, ontoDataPropertiesList, JSPropertyType, jsonschema, ontoClasses)
                    
                    if okRule2 or okRule3:
                        continue
                    
                    raise ValueError(f"Possible errors: {posibleArrayErrors}")
                else:
                    # Rule 3: an object property is mapped to an ontology property   
                    okRule3, possibleErrors = validateRule3And4(jsonMappedKey, ontoValue, mappedClasses, ontoObjectPropertiesList, "",None, ontoClasses)
                    if okRule3:
                        continue
                    else:
                        raise ValueError(f"Possible errors: {possibleErrors}")
        except Exception as e:
            print("ERROR processing key:", jsonMappedKey, "value:", ontoValue, "error:", e)
            raise e
    
    originalMappingJson = mapping
    print("## Final mapping: ", originalMappingJson, "##")
    return None

# Aparentemente esta validación estaría funcionando ok
# validateRule1 checks if the mappedTo iri is in the ontology classes and append the mapped class Iri to the mappedClasses dict
def validateRule1(key, ontoValuesMappedTo, ontoClasses):
    print("Enters Validate Rule 1")
    mappedIris = []
    for ontoElem in ontoValuesMappedTo:
        ontologyClassIri = ontoElem['iri']
        if not isIriInOntologyElem(ontologyClassIri, ontoClasses):
            raise ValueError(f"Element {ontologyClassIri} not found in ontology classes")
        else :
            print("## Found ontology class:", ontoElem['name'], "with iri: ",ontologyClassIri, "##")
            mappedIris.append(ontologyClassIri)

    return mappedIris

# IsMappedToOP checks if the the first mapped iri is an object property
def IsMappedToOP(ontoValuesMappedTo, ontoObjectProperties):
    ontoValues = list(ontoValuesMappedTo)
    firstMappedIri = ontoValues[0]['iri']
    if isIriInOntologyElem(firstMappedIri, ontoObjectProperties):
        return True
    else :
       return  False


# validateRule3And4 recieves the json-schema key, the ontology values mapped to and all valid ontolgy object properties. Then it does the next validations: 
# 1. checks if the ontology value is an existent objet property 
# 2. checks if the domain of the object property is already correctly mapped (by checking if it is in the mappedClasses dict)
# 3. checks if the range of the object property is already correctly mapped. If it isn't it maps it to the correct class and adds it to the newMappedClasses
# then at the end of all mapping iteration it adds the new mapped elements to the mapping json.
def validateRule3And4(key, ontoValuesMappedTo, mappedClasses, ontoObjectProperties, JSONPropertyType, jsonschema: JsonSchema, ontoClasses):
    possibleErrors = []
    print("### Validating rule 3: ", key, "##", ontoValuesMappedTo, "###")
    for ontoElem in ontoValuesMappedTo:
        isDomainOk = False
        isRangeOk = False
        ontologyProperty = ontoElem["iri"]
        domainName = getParentProperty(key)
        rangeName =  getSonProperty(key)
        # ojo porque esto es una lista! (ya que una property del json puede haber sido mapeado a varias clases)
        domainIrisList = mappedClasses.get(domainName, None)     
        rangeIrisList = mappedClasses.get(rangeName, None)
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
            print("Searching domain of object property: ", objectProperty.name)
            return False, possibleErrors
        
        if JSONPropertyType == "array":
            print("validating array")
            # obteno las properties del schema
            propType = "object"
            # valido que todas son tipos simpels
            isOk = checkAllJsonaSchemaTypes(jsonschema, key, propType)
            if not isOk:
                possibleErrors.append(f"If you're mapping {key} to a objectProperty all the types of the array must be objects")
                return False, possibleErrors
        # quedaríamos solo con esto, que el rango ya viene mapeado
        # si tengo un array igualmente tengo que haber mapeado previamente el elemento
        # lo identifico con la key del array
        for rangeIri in rangeIrisList:
            isRangeOk = isIriInOntologyElem(rangeIri, objectProperty.range)
            if isRangeOk:
                # si alguna de las clases del rango esta mapeada ya estoy OK
                break

        if not isRangeOk:
            print("ABOUT TO CHECK ANCESTORS of range: ", objectProperty.range)
            rangeMappedClass = getOntoPropertyByIri(rangeIri, ontoClasses)
            isRangeAnAncestor = checkAncestors(rangeMappedClass, objectProperty.range)
            if isRangeAnAncestor:
                isRangeOk = True
            if not isRangeAnAncestor:
                possibleErrors.append(f"Element {rangeIri} not found in object property range")
                return False, possibleErrors
            
        print("##isDomainOk: ", isDomainOk)
        print("##isRangeOk: ", isRangeOk)
        print("##Possible Errors: ", possibleErrors)
    return isDomainOk and isRangeOk, possibleErrors

# validateRule2And4 recieves the json-schema key, the ontology values mapped to and all valid ontolgy data properties. Then it does the next validations:
# 1. checks if the ontology value is an existent data property
# 2. checks if the domain of the data property is already correctly mapped (by checking if it is in the mappedClasses dict)
def validateRule2And4(key, ontoValuesMappedTo, mappedClasses, ontoDataProperties, JSONPropertyType, jsonschema: JsonSchema, ontoClasses):
    print("### Validating rule 2: ", key, "##", ontoValuesMappedTo, "###")
    possibleErrors = []
    isRangeOk = True
    for ontoElem in ontoValuesMappedTo:
        ontologyPropertyIri = ontoElem["iri"]
        # movie-name-string
        domainName = getParentProperty(key)
        # domain name = movie

        print("Domain name: ", domainName) # Thing
        domainIrisList = mappedClasses.get(domainName, None)
        print("DOMAIN IRIS LIST: ", domainIrisList)
        if domainIrisList is None:
            possibleErrors.append(f"Element {domainIrisList} not mapped to a class")
            return False, possibleErrors
        
        dataProperty = getOntoPropertyByIri(ontologyPropertyIri, ontoDataProperties)
        # rdf:label, domain: Thing
        if dataProperty is None:
            possibleErrors.append(f"Element {ontologyPropertyIri} not found in ontology data properties")
            return False, possibleErrors

        for domainIri in domainIrisList:
            # Aca tendriamos:
            # domainIri = movie iri movie
            # dataProperty.domain = Thing
            domainMappedClass = getOntoPropertyByIri(domainIri, ontoClasses)
            isDomainOk = isIriInOntologyElem(domainIri, dataProperty.domain)         
            if isDomainOk:
                break
        
        if not isDomainOk:
            print("ABOUT TO CHECK ANCESTORS of domain: ", dataProperty.domain)
            isDomainAnAncestor = checkAncestors(domainMappedClass, dataProperty.domain)
            if not isDomainAnAncestor:
                possibleErrors.append(f"Element {domainIri} is not an ancestor of {dataProperty.domain}")
                return False, possibleErrors
            
        if not isDomainOk and not isDomainAnAncestor:
            possibleErrors.append(f"Element {domainIri} not found in data property domain")
            return False, possibleErrors
        
        # si estoy validando un mapeo de array a dp tiene que cumplir que todos sus tipos son simples
        if JSONPropertyType == "array":
            print("validating array")
            # obteno las properties del schema
            propType = "simple"
            # valido que todas son tipos simpels
            isOk = checkAllJsonaSchemaTypes(jsonschema, key, propType)
            if not isOk:
                possibleErrors.append(f"If you're mapping {key} to a dataproperty, all the types of the array must be simple")
                return False, possibleErrors
        
    return isRangeOk, possibleErrors

# mover esta función

def checkAncestors(domainMappedClass, wantedAncestorClasses):
    for wantedAncestorClass in wantedAncestorClasses:
        for ancestor in domainMappedClass.ancestors():
            print("ANCESTOR: ", ancestor)
            if ancestor.iri == wantedAncestorClass.iri:
                print("FOUND ANCESTOR: ", ancestor)
                return True
    return False


def checkAllJsonaSchemaTypes( jsonSchema: JsonSchema, key, propType):
    print("JSONSCHEMA: ", jsonSchema)
    jsonSchema = JsonSchema(**jsonSchema)
    propertyBeingLooked = jsonSchema.findPropertyInJsonSchema(key)
    print("paso")
    print("## Property being looked: ", propertyBeingLooked, "##")
    if(propertyBeingLooked is None):
        print("## Property being looked is None ##")
    if propertyBeingLooked["type"] != "array":
        return False
    items = propertyBeingLooked["items"]
    print("Items: ", items)
    print("Prop Type: ", propType)
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
        print("## Onto property: ", obj_prop, "##")
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
    son = jsonKey.split(mapping_type_separator)[0]
    # se deja como hijo toda la cadena, por si hay elementos repetidos
    # es decir de "destination-accomodation-ratings_key" el hijo es "destination-accomodation-ratings"
    print("## Son property: ", son, "##")
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

# valores posibles que retorna = string, int, bool, float, array
# con esto nos dice si el mapping es una dataproperty o no
# destion-accomodation_key#string
def getJsonSchemaPropertieType(str):
    print("## Getting JSON Schema Property Type ##")
    splittedMappingKey = str.split(mapping_type_separator)
    keyPart = splittedMappingKey[1]
    hashTag = keyPart.split("#")
    print("hashTag", hashTag)
    if len(hashTag) > 1:
        return hashTag[1]
    return ""
    
def checkRangeAndJSONDataProperty(JSONProperty, ontoRange):
    if (str(JSONProperty) == "string" and ontoRange == str) or (str(JSONProperty) == "int" and ontoRange == int) or (str(JSONProperty) == "bool" and ontoRange == bool) :
        return True
    
    return False

# mover para otro file pero dentro de este mismo modulo

# find_json_keys gets the key of a mapping structure for example "#contacto-city_key#string", and returns 
# a lis of the json keys of that entry: ['contacto','city'], this means that 'city' its an attribute inside 'contacto'
def find_json_keys(path) :
    print(f'path ${path}') #contacto-city?key#string
    # TODO-change-serparador
    keys = path.replace('-', mapping_type_separator).split(mapping_type_separator)
    print(f'keys ${keys}')

    json_keys = keys[:-1] 
    json_keys.remove('rootObject')
    return json_keys

# esta función busca un elemento en un json a partir de un path dado por la entrada del mapping
# destination-accomodation-name
# accomodation aca puedo recibir value
# TODO: ver posibilidad de obtener el nodo FIELD, aprovechando la anidación entre los campos del json
def find_element_in_JSON_instance(json_document, path) :
    print(f'json_document ${json_document}')
    print(f'path ${path}') #contacto-city_key#string
    # TODO-change-serparador
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