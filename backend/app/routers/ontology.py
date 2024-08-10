from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import shutil
from owlready2 import get_ontology
from app.domain.mapping.models import MappingProcessDocument, OntologyDocument
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from typing import Optional, List
import os

username = "Cluster04367"
password = "23deagosto8"
uri = 'mongodb+srv://' + username + ':' + password + '@cluster04367.44sngv1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster04367'

router = APIRouter()


client = AsyncIOMotorClient(uri)
db = client.proyecto_grado

onto_collection = db.get_collection("ontologies")
mapping_process_collection = db.get_collection("mapping_process")

#async def checkConnection():
    #try:
        
    #except Exception as e:
        #print(f"Error de conexión: {e}")
        

#@router.get("/check-db/")
#async def check_db():
    #await checkConnection()

toDirectory = "upload/ontologies"
@router.post("/")
# revisar, capaz no es necasario guardar la onto en mongo db 
async def upload_ontology(type: str = Form(...), ontology_file: UploadFile = File(...), uri: Optional[str] = Form(None)):
    try:
        if not os.path.exists(toDirectory):
            os.makedirs(toDirectory)

        completePath = os.path.join(toDirectory, ontology_file.filename)
        with open(completePath, "wb") as f:
            ontology_content = await ontology_file.read()
            f.write(ontology_content)
        
        ontoDocu = OntologyDocument(type=type, file=completePath)
        print("about to insert")

        result = await onto_collection.insert_one(ontoDocu.dict())
        print("inserted corretcly")
        ontology_id = result.inserted_id

        mapping_process_docu = MappingProcessDocument(id=None, ontologyId=str(ontology_id), mapping={}, jsonSchemaId=None)   
        mapping_process_result = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))
        mapping_process_id = mapping_process_result.inserted_id

        print("inserted correctly with id", mapping_process_id)
        
        # en esta parte se obtiene la ontología y se devuelven sus partes para mostrarlas en el front
        ontology = get_ontology(completePath).load()
        classes = list(ontology.classes())
        
        object_properties = list(ontology.object_properties())
        data_properties = list(ontology.data_properties())
        ontology_data = {
            "mapping_process_id": str(mapping_process_id),
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