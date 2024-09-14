from fastapi import APIRouter, HTTPException, Query, Body
from bson import ObjectId
from owlready2 import get_ontology
import motor.motor_asyncio
from app.domain.mapping.utils import get_ontology_info_from_pid, graph_generator
from app.domain.mapping.models import MappingProcessDocument, EditMappingRequest, MappingRequest, MappingResponse, OntologyDocument, JsonSchema
from app.domain.mapping.service import process_mapping
from app.domain.dataquality.evaluation import StrategyContext
from ..database import onto_collection, mapping_process_collection, jsonschemas_collection
from typing import List, Optional, Dict, Any


from genson import SchemaBuilder
from pydantic import BaseModel

router = APIRouter()

class JsonRequest(BaseModel):
    json_data: dict

@router.post("/generate-schema/")
async def generate_schema(request: JsonRequest):
    try:
        builder = SchemaBuilder()
        builder.add_object(request.json_data)
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class JsonRequestList(BaseModel):
    json_data: List[dict]  # Cambiado para aceptar una lista de JSON

@router.post("/generate-schemaList/")
async def generate_schema(request: JsonRequestList):
    try:
        builder = SchemaBuilder()
        for json_obj in request.json_data:
            builder.add_object(json_obj)
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#  seed_schema = {'type': 'array', 'items': []}
# >>> builder.add_schema(seed_schema)

@router.post("/ontology_id/{ontology_id}", response_model=MappingResponse)
async def save_mapping(ontology_id: str, request: MappingRequest = Body(...)):
    try:
        print("Starting ontology saving 1")
        onto_id = ObjectId(ontology_id)
        ontology_docu = await onto_collection.find_one({'_id': onto_id})
        
        if ontology_docu is None:
            raise HTTPException(status_code=404, detail="Ontology not found")
        
        # Validate the mapping field
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="Invalid mapping body")
        
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)
        print("Starting ontology saving 1")
        if ontology_document.type == "FILE":
            ontology_path = ontology_document.file
            ontology = get_ontology(ontology_path).load()
        else:
            ontology = get_ontology(str(ontology_document.uri)).load()
        # saving json schema
        schema_dict = request.jsonSchema

        schema_result = await jsonschemas_collection.insert_one(schema_dict)
        schema_id = schema_result.inserted_id

        # here we validate if the mapping is correct
        status = process_mapping(request.mapping, ontology, request.jsonSchema)
        print("validation OK")

        # saving mapping process
        mapping = request.mapping
        mapping_process_docu = MappingProcessDocument(name=request.name, mapping=mapping, ontologyId=ontology_id,jsonSchemaId=str(schema_id))
        mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))
     
        return MappingResponse(message="Mapped successfully", status="success",mapping_id=str(mapping_pr_id.inserted_id))
    except ValueError as e:
        msg = str(e)
        status = "error"
        response = MappingResponse(message=msg, status="error")
        return response
    except Exception as e:
        print("Error saving mapping process:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mapping_process_id}")
async def get_mapping(mapping_process_id: str):
    try:
        mapping_pr_id = ObjectId(mapping_process_id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_pr_id})
        mappingProcessDocu = MappingProcessDocument(**mapping_process_docu)
        print("mappingProcessDocu", mappingProcessDocu)
        # TERMINAR ##
        onto_id = mappingProcessDocu.ontologyId
        ontology_id = ObjectId(onto_id)
        ontology = await onto_collection.find_one({'_id': ontology_id})
        ontology_path = ontology.get('file')
        print("ontology_path", ontology_path)
        # Mover esto para un lugar más adecuado
        ontology = get_ontology(ontology_path).load()
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
            'mapping': mappingProcessDocu.mapping,
            'mapping_name': mappingProcessDocu.name
        }

        print("complete_mapping", complete_mapping)
        return complete_mapping
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response


@router.get("/graph/{process_id}", response_model = Any)
async def get_graph(process_id: str):
    try:
        pid = ObjectId(process_id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': pid})
        onto_for_graph = await get_ontology_info_from_pid(mapping_process_docu['ontologyId'])
        graph_with_mappings = graph_generator(onto_for_graph, mapping_process_docu['mapping'])
        
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal error while generating the graph ")
    
    return graph_with_mappings

@router.get("/" )
async def get_mappings():
    try :
        mapping_docus =  mapping_process_collection.find({})
        mapping_process_docs = await mapping_docus.to_list(length=None)  
        mappingpr_names = []
        for mapping_process_doc in mapping_process_docs:
            print("Mapping process doc", mapping_process_doc)
            mappingpr = {
                "id": str(mapping_process_doc['_id']),
                "name": mapping_process_doc['name'],
            }
            mappingpr_names.append(mappingpr)
        print("Mappings", mappingpr_names)
        return mappingpr_names
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response



@router.put("/{mapping_process_id}")
async def put_mapping(mapping_process_id: str, request: MappingRequest = Body(...)):
    try:
        mapping_pr_id = ObjectId(mapping_process_id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_pr_id})
        if not mapping_process_docu:
            return MappingResponse(message="Mapping process not found", status="error")
        
        update_data = {}
        for key, value in request.model_dump().items():
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


# @router.get("/evaluate/{mapping_process_id}" )
# async def evaluate_dq(mapping_process_id: str) : 
#     await evaluate_data_quality("path", mapping_process_id)

# /evaluate/syntactic_accuracy?mapping_process_id=123
@router.post("/evaluate/{quality_rule}")
async def evaluate_quality(quality_rule: str, mapping_process_id: Optional[int] = Query(None, description="ID for mapping"), request_mapping_body:Dict[str, Any]= Body(...)) :
    try :
        context = StrategyContext()
        context.select_strategy(quality_rule)
        

        context.evaluate_quality(mapping_process_id, request_mapping_body)
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response