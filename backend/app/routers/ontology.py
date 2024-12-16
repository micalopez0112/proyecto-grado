
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from owlready2 import get_ontology
from typing import Optional, List, Any

from ..database import onto_collection
from app.models.ontology import OntologyDocument
from app.services import ontology_service as onto_service
from app.rules_validation.utils import get_ontology_info_from_pid, graph_generator

import os

router = APIRouter()

toDirectory = "upload/ontologies"
@router.post("/")
async def upload_ontology(type: str = Form(...), ontology_file: Optional[UploadFile] = File(None), uri: Optional[str] = Form(None)):
    try:
        ontology_data = await onto_service.save_ontology(type, ontology_file, uri)
        return JSONResponse(content={
            "message": "Ontology loaded and processed successfully",
            "ontologyData": ontology_data
        })
    except Exception as e:
        print("Error processing ontology:", e)
        raise HTTPException(status_code=500, detail=str(e))

#Retrieves the graph structure of an ontology
@router.get("/ontology-graph/{ontology_id}", response_model = Any)
async def get_ontology_graph(ontology_id: str):
    try:
        onto_for_graph = await get_ontology_info_from_pid(ontology_id)
        graph = graph_generator(onto_for_graph, {})
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal error while generating the graph ")
    return graph

# Borrar luego 
@router.get("/", response_model=List[OntologyDocument])
async def get_ontologies():
    try:
        # Encuentra todos los documentos en la colección
        documents = await onto_collection.find().to_list(length=100)  # Ajusta el valor de length según sea necesario
        # Convierte ObjectId a cadena en los documentos
        for doc in documents:
            doc['id'] = str(doc['_id'])
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ontologías: {e}")
    
#Retrieves the graph structure of an ontology
@router.get("/{ontology_id}", response_model = Any)
async def get_ontology_by_id(ontology_id: str):
    try:
        ontology = await onto_service.get_ontology_by_id(ontology_id)
        ontology_data = onto_service.build_ontology_response(ontology, ontology_id)
    
        return ontology_data
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal error while generating the graph ")
    
    return graph
   