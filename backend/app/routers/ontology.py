import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from owlready2 import get_ontology
from typing import Optional, List
from app.domain.mapping.models import MappingProcessDocument, OntologyDocument
from ..database import onto_collection


router = APIRouter()

toDirectory = "upload/ontologies"
@router.post("/")
async def upload_ontology(type: str = Form(...), ontology_file: UploadFile = File(...), uri: Optional[str] = Form(None)):
    try:
        if not os.path.exists(toDirectory):
            os.makedirs(toDirectory)

        completePath = os.path.join(toDirectory, ontology_file.filename)
        with open(completePath, "wb") as f:
            ontology_content = await ontology_file.read()
            f.write(ontology_content)
        
        ontoDocu = OntologyDocument(type=type, file=completePath)
        result = await onto_collection.insert_one(ontoDocu.dict())
        ontology_id = result.inserted_id

        # en esta parte se obtiene la ontología y se devuelven sus partes para mostrarlas en el front
        ontology = get_ontology(completePath).load()
        classes = list(ontology.classes())
        object_properties = list(ontology.object_properties())
        data_properties = list(ontology.data_properties())
        ontology_data = {
            "ontology_id": str(ontology_id),
            "ontoData": [{
                "name": ontology_file.filename,
                "data": [{
                    "classes": [{"name": cls.name, "iri": cls.iri} for cls in classes],
                    "object_properties": [{"name": prop.name, "iri": prop.iri} for prop in object_properties],
                    "data_properties": [{"name": prop.name, "iri": prop.iri} for prop in data_properties]
                }]
            }]
        }

        return JSONResponse(content={
            "message": "File uploaded and processed successfully",
            "ontologyData": ontology_data
        })
    except Exception as e:
        print("Error saving :", e)
        raise HTTPException(status_code=500, detail=str(e))

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