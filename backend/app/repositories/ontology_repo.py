from ..database import  onto_collection
from app.models.ontology import  OntologyDocument
from bson import ObjectId
from app.repositories.metadata_repo import insert_context_metadata

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
    onto_model_data = ontology_document.model_dump()
    if(onto_model_data.get('uri')):
        onto_model_data['uri'] = str(onto_model_data['uri'])
        onto_name = onto_model_data['uri']
    else:
        onto_name = onto_model_data['file'].split('/')[-1]
    result = await onto_collection.insert_one(onto_model_data)
    inserted_onto_id = str(result.inserted_id)
    insert_context_metadata(inserted_onto_id, onto_name)
    return inserted_onto_id

async def delete_ontology_by_id(ontology_id: str) -> bool:
    ontology_object_id = ObjectId(ontology_id)
    result = await onto_collection.delete_one({"_id": ontology_object_id})
    return result
   
