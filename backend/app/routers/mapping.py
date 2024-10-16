from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
import json
from bson import ObjectId
from owlready2 import get_ontology

from app.domain.mapping.service import getJsonSchemaPropertieType
from app.domain.mapping.utils import get_ontology_info_from_pid, graph_generator
from app.domain.mapping.models import MappingProcessDocument, EditMappingRequest, MappingRequest, MappingResponse, OntologyDocument, JsonSchema, PutMappingRequest
from app.domain.mapping.service import process_mapping
from app.domain.dataquality.evaluation import StrategyContext
from ..database import onto_collection, mapping_process_collection, jsonschemas_collection
from typing import List,Optional, Dict, Any

from genson import SchemaBuilder
from pydantic import BaseModel

router = APIRouter()

class JsonRequest(BaseModel):
    jsonInstances: dict

@router.post("/generate-schema/")
async def generate_schema(request: JsonRequest):
    try:
        builder = SchemaBuilder()
        builder.add_object(request.jsonInstances)
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class JsonRequestList(BaseModel):
    jsonInstances: List[dict]  # Cambiado para aceptar una lista de JSON


@router.post("/generate-schemaList/")
async def generate_schema(request: JsonRequestList):
    try:
        builder = SchemaBuilder()
        for json_obj in request.jsonInstances:
            builder.add_object(json_obj)
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

        
@router.post("/generate-schemaListFromFiles/")
async def generate_schema(request: List[UploadFile] = File(...)):
    try:
        builder = SchemaBuilder()
        for file in request:
            content = await file.read() 
            json_data = json.loads(content)
            builder.add_object(json_data) 
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#  seed_schema = {'type': 'array', 'items': []}
# >>> builder.add_schema(seed_schema)

@router.post("/ontology_id/{ontology_id}", response_model = MappingResponse)
async def save_mapping(ontology_id: str, mapping_proccess_id: str | None = None, 
                       request: MappingRequest = Body(...)):
    try:
        print("Mapping_process_id: ", mapping_proccess_id)
        # print("#REQUEST#: ", request);
        onto_id = ObjectId(ontology_id)
        ontology_docu = await onto_collection.find_one({'_id': onto_id})
        
        if ontology_docu is None:
            raise HTTPException(status_code=404, detail="Ontology not found")
        
        # Validate the mapping field
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="Invalid mapping body")
        
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)
        if ontology_document.type == "FILE":
            ontology_path = ontology_document.file
            ontology = get_ontology(ontology_path).load()
        else:
            ontology = get_ontology(str(ontology_document.uri)).load()
            
        if (mapping_proccess_id is not None):
            #case when updating a mapping process
            editRequest = EditMappingRequest(name=request.name, mapping=request.mapping)
            mapping_pr_id = ObjectId(mapping_proccess_id)
            mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_pr_id})
            if not mapping_process_docu:
                return MappingResponse(message="Mapping process not found", status="error")
            
            #saving(editing) mapping process
            update_data = {'mapping_suscc_validated': False}
            for key, value in editRequest:#request.model_dump().items():
                print("value", value)
                if value is not None and value != "" and value != {} and value != "string":
                    update_data[key] = value
        
            queryTOUpdate = {'_id': mapping_pr_id}
            tryUpdate =  {'$set': update_data}
            result = await mapping_process_collection.update_one(
                queryTOUpdate,
                tryUpdate
            )
            
            # here we validate if the mapping is correct
            status = process_mapping(request.mapping, ontology, request.jsonSchema)
            print("Validation OK")

            print("Update mapping proccess to be valid:", mapping_proccess_id)
            #updates the inserted mapping_process with the validation status
            
            update_data = {'mapping_suscc_validated': True}
            tryUpdate =  {'$set': update_data}
            result = await mapping_process_collection.update_one(
                queryTOUpdate,
                tryUpdate
            )
            return MappingResponse(message="Mapping saved and validated successfully",
                                    status="success",mapping_id=mapping_proccess_id)
            #catch any more exception ?
        else:
            #case when saving a mapping process for the first time
            # saving json schema
            schema_dict = request.jsonSchema
            schema_result = await jsonschemas_collection.insert_one(schema_dict)
            schema_id = schema_result.inserted_id

            # saving whole mapping process
            mapping = request.mapping
            name = request.name
            mapping_process_docu = MappingProcessDocument(name=name, mapping=mapping,
                                                           ontologyId=ontology_id,
                                                           jsonSchemaId=str(schema_id),
                                                           mapping_suscc_validated=False)
            mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))

             # here we validate if the mapping is correct
            status = process_mapping(request.mapping, ontology, request.jsonSchema)

            #updates the inserted mapping_process with the validation status
            mapping_id = str(mapping_pr_id.inserted_id)
            mapping_pr_id = ObjectId(mapping_pr_id.inserted_id)
            update_data = {'mapping_suscc_validated': True}

            queryTOUpdate = {'_id': mapping_pr_id}
            tryUpdate =  {'$set': update_data}
            result = await mapping_process_collection.update_one(
                queryTOUpdate,
                tryUpdate
            )
            #print("validation OK")
            return MappingResponse(message="Mapped successfully", status="success",mapping_id=mapping_id)
    except ValueError as e:
        msg = str(e)
        status = "error"
        response = MappingResponse(message=msg, status="error")
        return response
    except Exception as e:
        print("Error saving mapping process:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
async def put_mapping(request: PutMappingRequest = Body(...)):
    try:
        print("REQUEST DEL PUT: ", request);
        if(request.mapping_proccess_id is None or request.mapping_proccess_id == ""):
            #case when saving a mapping process for the first time
            print("Create and return mapping_proccess_id")
            ontology_id = request.ontology_id
            onto_id = ObjectId(ontology_id)
            ontology_docu = await onto_collection.find_one({'_id': onto_id})
            
            if ontology_docu is None:
                raise HTTPException(status_code=404, detail="Ontology not found")
            
            # Validate the mapping field
            if not isinstance(request.mapping, dict):
                raise HTTPException(status_code=400, detail="Invalid mapping body")
            
            ontology_docu['id'] = str(ontology_docu['_id'])
            ontology_document = OntologyDocument(**ontology_docu)
            if ontology_document.type == "FILE":
                ontology_path = ontology_document.file
                ontology = get_ontology(ontology_path).load()
            else:
                ontology = get_ontology(str(ontology_document.uri)).load()
            # saving json schema
            schema_dict = request.jsonSchema
            schema_result = await jsonschemas_collection.insert_one(schema_dict)
            schema_id = schema_result.inserted_id

            # saving mapping process
            mapping = request.mapping
            name = request.name
            mapping_process_docu = MappingProcessDocument(name=name, mapping=mapping,
                                                           ontologyId=ontology_id,
                                                           jsonSchemaId=str(schema_id),
                                                           mapping_suscc_validated=False)
            mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))
            return MappingResponse(message="Mapping process saved successfully", status="success",mapping_id = str(mapping_pr_id.inserted_id))
        
        else:
            #case when updating a mapping process (mapping_process_id is provided)
            print("Update mapping_proccess_id: ", request);
            mapping_process_id = request.mapping_proccess_id
            editRequest = EditMappingRequest(name=request.name, mapping=request.mapping)
            mapping_pr_id = ObjectId(mapping_process_id)
            mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_pr_id})
           
            if not mapping_process_docu:
                return MappingResponse(message="Mapping process not found", status="error")
            
            update_data = {'mapping_suscc_validated': False}
            for key, value in editRequest.model_dump().items():#request.model_dump().items():
                print("value", value)
                if value is not None and value != "" and value != {} and value != "string":
                    update_data[key] = value
        
            queryTOUpdate = {'_id': mapping_pr_id}
            tryUpdate =  {'$set': update_data}
            result = await mapping_process_collection.update_one(
                queryTOUpdate,
                tryUpdate
            )
            return MappingResponse(message="Mapping process updated successfully", status="success",mapping_id = mapping_process_id)
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response


@router.get("/{mapping_process_id}")
async def get_mapping(mapping_process_id: str, filter_dp: Optional[bool] = None):
    try:
        mapping_pr_id = ObjectId(mapping_process_id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_pr_id})
        mappingProcessDocu = MappingProcessDocument(**mapping_process_docu)
        print("mappingProcessDocu", mappingProcessDocu)
        
        if(filter_dp is not None and filter_dp == True):
            # Filter mapping_process to retrieve only data properties components
            mapping = mappingProcessDocu.mapping
            mapping = {k: v for k, v in mapping.items() if (getJsonSchemaPropertieType(k) != '') }#not v.get('isDataProperty')}
            print("Ver si funcionó el mapping", mapping)
            #getJsonSchemaPropertieType
            ##mappingProcessDocu.mapping = mapping
        # TERMINAR ##
        else:
            mapping = mappingProcessDocu.mapping

        onto_id = mappingProcessDocu.ontologyId
        ontology_id = ObjectId(onto_id)
        ontology = await onto_collection.find_one({'_id': ontology_id})
        if ontology.get('type') == "FILE":
            ontology_path = ontology.get('file')
            print("ontology_path", ontology_path)
            # Mover esto para un lugar más adecuado
            ontology = get_ontology(ontology_path).load()
        else:
            ontology_uri = ontology.get('uri')
            print("ontology_uri", ontology_uri)
            ontology = get_ontology(str(ontology_uri)).load()
        classes = list(ontology.classes())
        object_properties = list(ontology.object_properties())
        data_properties = list(ontology.data_properties())
        ontology_data = {
            "ontology_id":onto_id,
            "ontoData": [{
                "data": [{
                    "classes": [{"name": cls.name, "iri": cls.iri} for cls in classes],
                    "object_properties": [{"name": prop.name, "iri": prop.iri,"range":{"name":range.name,"iri":range.iri}} for prop in object_properties for range in prop.range],
                    "data_properties": [{"name": prop.name, "iri": prop.iri} for prop in data_properties]
                }]
            }]
        }
        # Recuperar la información del schema asociado
        sh_id = mappingProcessDocu.jsonSchemaId
        schema_id = ObjectId(sh_id)
        schemaDocum = await jsonschemas_collection.find_one({'_id': schema_id})
        JSONSchema = JsonSchema(**schemaDocum)

        # AJUSTAR
        complete_mapping = {
            'ontology': ontology_data,
            'schema': JSONSchema,
            'mapping': mapping,
            'mapping_name': mappingProcessDocu.name
        }

        #print("complete_mapping", complete_mapping)
        return complete_mapping
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response

@router.get("/" )
async def get_mappings(validated_mappings: Optional[bool] = None) :
    try :
        if((validated_mappings is not None) and (validated_mappings == True)):
            mapping_docus =  mapping_process_collection.find({'mapping_suscc_validated': True})
        else:
            mapping_docus =  mapping_process_collection.find({})
        mapping_process_docs = await mapping_docus.to_list(length=None)  
        mappingpr_names = []
        for mapping_process_doc in mapping_process_docs:
            #print("Mapping process doc", mapping_process_doc)
            mappingpr = {
                "id": str(mapping_process_doc['_id']),
                "name": mapping_process_doc['name'],
            }
            mappingpr_names.append(mappingpr)
        #print("Mappings", mappingpr_names)
        return mappingpr_names
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response

# @router.get("/evaluate/{mapping_process_id}" )
# async def evaluate_dq(mapping_process_id: str) : 
#     await evaluate_data_quality("path", mapping_process_id)

# /evaluate/syntactic_accuracy?mapping_process_id=123
@router.post("/evaluate/{quality_rule}")
async def evaluate_quality(quality_rule: str, mapping_process_id: Optional[str] = Query(None, description="ID for mapping"), request_mapping_body: Dict[str, Any]= Body(...)) :
    print(f'request_mapping_body: {request_mapping_body}')
    try :
        context = StrategyContext()
        context.select_strategy(quality_rule)
        
        await context.evaluate_quality(mapping_process_id, request_mapping_body)
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
