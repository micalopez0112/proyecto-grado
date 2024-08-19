from app.domain.mapping.models import JsonSchema

VALUE = "value"
KEY = "key"

simpleTypes = ["string", "int", "bool", "float"]
# TODO: revisar el tema del orden, mirar la tesis de aquellos para ver como hacian, ahora como esta hecho 
# se asume que todos los mapeos de clases vienen primero.!!
# ahora toma el mappingProcess por parámetro pero estaría guardado en una db
# ojo ver si este tipado funciona
def process_mapping(mapping, ontology, jsonschema: JsonSchema):
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
        # en principio tomo como el mapeo es uno solo pero si es una lista seria recorer los elementos e ir aplicando la regla
        try :
            if isJSONValue(jsonMappedKey):
                # Rule 1: an object is mapped to an ontology class
                mappedIris = validateRule1(jsonMappedKey, ontoValue, ontoClasses)
                mappedClassKey = jsonMappedKey.split("_")[0]
                mappedClasses[mappedClassKey] = mappedIris
                print("## Mapped OK ##", mappedClasses)             
            if isJSONKey(jsonMappedKey):              
                # Rule 2: a simple property is mapped to an ontology data property
                JSPropertyType = getJsonSchemaPropertieType(jsonMappedKey)
                if JSPropertyType != "" and (JSPropertyType in simpleTypes):
                    print("is data property mapping")
                    okRule2, possibleRule2Errors = validateRule2And4(jsonMappedKey, ontoValue, mappedClasses, ontoDataPropertiesList, JSPropertyType, None)
                    if not okRule2:
                        possibleErrors.extend(possibleRule2Errors)
                        raise ValueError(f"Possible errors: {possibleErrors}")
                elif JSPropertyType != "" and (JSPropertyType == "array"):
                    posibleArrayErrors = []
                    # acomodar
                    if IsMappedToOP(ontoValue, ontoObjectPropertiesList):
                        okRule3, posibleArrayErrors = validateRule3And4(jsonMappedKey, ontoValue, mappedClasses, ontoObjectPropertiesList, JSPropertyType,jsonschema) 
                    else :
                        okRule2, posibleArrayErrors = validateRule2And4(jsonMappedKey, ontoValue, mappedClasses, ontoDataPropertiesList, JSPropertyType, jsonschema)
                    
                    if okRule2 or okRule3:
                        continue
                    
                    raise ValueError(f"Possible errors: {posibleArrayErrors}")
                else:
                    # Rule 3: an object property is mapped to an ontology property   
                    okRule3, possibleErrors = validateRule3And4(jsonMappedKey, ontoValue, mappedClasses, ontoObjectPropertiesList, "",None)
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
def validateRule3And4(key, ontoValuesMappedTo, mappedClasses, ontoObjectProperties, JSONPropertyType, jsonschema: JsonSchema):
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
            possibleErrors.append(f"Element {rangeIri} not found in object property range")
            return False, possibleErrors

    return isDomainOk and isRangeOk, possibleErrors

# validateRule2And4 recieves the json-schema key, the ontology values mapped to and all valid ontolgy data properties. Then it does the next validations:
# 1. checks if the ontology value is an existent data property
# 2. checks if the domain of the data property is already correctly mapped (by checking if it is in the mappedClasses dict)
def validateRule2And4(key, ontoValuesMappedTo, mappedClasses, ontoDataProperties, JSONPropertyType, jsonschema: JsonSchema):
    print("### Validating rule 2: ", key, "##", ontoValuesMappedTo, "###")
    possibleErrors = []
    isRangeOk = True
    for ontoElem in ontoValuesMappedTo:
        ontologyPropertyIri = ontoElem["iri"]
        domainName = getParentProperty(key)
        print("DOMAIN NAME: ", domainName)

        domainIrisList = mappedClasses.get(domainName, None)
        print("DOMAIN IRIS LIST: ", domainIrisList)
        if domainIrisList is None:
            possibleErrors.append(f"Element {domainIrisList} not mapped to a class")
            return False, possibleErrors
        
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



def checkAllJsonaSchemaTypes( jsonSchema: JsonSchema, key, propType):
    print("JSONSCHEMA: ", jsonSchema)
    #jsonSchema = JsonSchema(**jsonschema)
    propertyBeingLooked = jsonSchema.findPropertyInJsonSchema(key)
    if propertyBeingLooked["type"] != "array":
        return False
    items = propertyBeingLooked["items"]
    for item in items:
        if propType == "simple" and item["type"] not in simpleTypes:
            return False
        if propType == "object" and item["type"] != "object":
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
        print("## Object property: ", obj_prop, "##")
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
    splittedMappingKey = str.split("_")
    return splittedMappingKey[1] == VALUE

def isJSONKey(str):
    splittedMappingKey = str.split("_")
    # if the mapping was done to a data property concatenated with a "-" next to the key comes the property type: 
    # example: "accomodation-ratings_key-string"
    keyPart = splittedMappingKey[1].split("#")
    return keyPart[0] == KEY



def isDataPropertyMapping(str):
    splittedMappingKey = str.split("_")
    keyPart = splittedMappingKey[1]
    hashTag = keyPart.split("#")
    if hashTag[1] in simpleTypes:
        return True
    return False

# valores posibles que retorna = string, int, bool, float, array
def getJsonSchemaPropertieType(str):
    splittedMappingKey = str.split("_")
    keyPart = splittedMappingKey[1]
    hashTag = keyPart.split("#")
    if len(hashTag) > 1:
        return hashTag[1]
    return ""
    
def checkRangeAndJSONDataProperty(JSONProperty, ontoRange):
    if (str(JSONProperty) == "string" and ontoRange == str) or (str(JSONProperty) == "int" and ontoRange == int) or (str(JSONProperty) == "bool" and ontoRange == bool) :
        return True
    
    return False