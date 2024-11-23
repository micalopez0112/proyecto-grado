
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
        ontology_id = ''
        if ontology_file:
            if not os.path.exists(toDirectory):
                os.makedirs(toDirectory)

            completePath = os.path.join(toDirectory, ontology_file.filename)
            with open(completePath, "wb") as f:
                ontology_content = await ontology_file.read()
                f.write(ontology_content)

            print("onto path", completePath)
            onto_in_collection = await onto_collection.find_one({"file": completePath})
            #check if the file already exists (search by completePath)

            ontology = get_ontology(completePath).load()
            ontology.imported_ontologies.append(get_ontology("http://www.w3.org/2000/01/rdf-schema"))
            if not onto_in_collection:    
                print("onto not in collection")
                ontoDocu = OntologyDocument(type=type, file=completePath)
            else:
                ontology_id = str(onto_in_collection['_id'])
        elif uri:
            # Manejo de la URI
            print("onto uri", uri)
            #check if the file already exists (search by uri)
            onto_in_collection = await onto_collection.find_one({"uri": uri})
            if not onto_in_collection:
                print("onto not in collection")
                ontoDocu = OntologyDocument(type=type, uri=uri)
            else:
                ontology_id = str(onto_in_collection['_id'])
            ontology = get_ontology(str(uri)).load()
        else:
            raise HTTPException(status_code=400, detail="No ontology file or URI provided")

        if(ontology_id == ''):
            result = await onto_collection.insert_one(ontoDocu.model_dump())
            ontology_id = result.inserted_id
            print("Inserted correctly - Ontology ID:", ontology_id)
        else:
            print("Ontology already exists - Ontology ID:", ontology_id)

        # Obtener las clases y propiedades de la ontología
        classes = list(ontology.classes())
        object_properties = list(ontology.object_properties())
        data_properties = list(ontology.data_properties())
        for dp in data_properties:
            print("### DP NAME: ###", dp.name)
            print("### DP DOMAIN: ###", dp.domain)

        print("Object Propertie", object_properties[0])
        ontology_data = {
            "ontology_id": str(ontology_id),
            "ontoData": [{
                "name": ontology_file.filename if ontology_file else uri,
                "data": [{
                    "classes": [{"name": cls.name, "iri": cls.iri} for cls in classes],
                    "object_properties": [{"name": prop.name, "iri": prop.iri, "range": {"name": range.name, "iri": range.iri}} for prop in object_properties for range in prop.range],
                    "data_properties": [{"name": prop.name, "iri": prop.iri} for prop in data_properties]
                }]
            }]
        }
        print("Ontology data", ontology_data);
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
   