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
async def upload_ontology(type: str = Form(...), ontology_file: Optional[UploadFile] = File(None), uri: Optional[str] = Form(None)):
    try:
        
        if ontology_file:
            if not os.path.exists(toDirectory):
                os.makedirs(toDirectory)

            completePath = os.path.join(toDirectory, ontology_file.filename)
            with open(completePath, "wb") as f:
                ontology_content = await ontology_file.read()
                f.write(ontology_content)

            print("onto path", completePath)
            ontoDocu = OntologyDocument(type=type, file=completePath)
            ontology = get_ontology(completePath).load()
        elif uri:
            # Manejo de la URI
            print("onto uri", uri)
            ontoDocu = OntologyDocument(type=type)
            ontology = get_ontology(str(uri)).load()
            ontoDocu.uri = uri
        else:
            raise HTTPException(status_code=400, detail="No ontology file or URI provided")

        result = await onto_collection.insert_one(ontoDocu.model_dump())
        ontology_id = result.inserted_id
        print("Inserted correctly - Ontology ID:", ontology_id)

        # Obtener las clases y propiedades de la ontología
        classes = list(ontology.classes())
        object_properties = list(ontology.object_properties())
        data_properties = list(ontology.data_properties())
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
        print("Ontology data", ontology_data)
        return JSONResponse(content={
            "message": "Ontology loaded and processed successfully",
            "ontologyData": ontology_data
        })
    except Exception as e:
        print("Error processing ontology:", e)
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
    

