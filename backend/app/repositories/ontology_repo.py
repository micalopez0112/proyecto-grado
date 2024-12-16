from ..database import  onto_collection
from app.models.ontology import  OntologyDocument
from bson import ObjectId

async def find_ontology_by_id(ontology_id: str):
    onto_id = ObjectId(ontology_id)
    ontology_docu = await onto_collection.find_one({'_id': onto_id})
    
    if ontology_docu is not None:   
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)

        return ontology_document
    return None

async def find_ontology_by_file_path(ontology_path: str):
    ontology_docu = await onto_collection.find_one({'file': ontology_path})
    if ontology_docu is not None:   
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)

        return ontology_document
    return None

async def find_ontology_by_uri(uri: str):
    ontology_docu = await onto_collection.find_one({'uri': uri})
    if ontology_docu is not None:   
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)
        return ontology_document
    return None

async def insert_ontology(ontology_document: OntologyDocument):
    result = await onto_collection.insert_one(ontology_document.model_dump())
    return str(result.inserted_id)

async def delete_ontology_by_id(ontology_id: str) -> bool:
    ontology_object_id = ObjectId(ontology_id)
    result = await onto_collection.delete_one({"_id": ontology_object_id})
    return result
   
