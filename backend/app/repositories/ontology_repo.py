from ..database import  onto_collection
from app.rules_validation.models import  OntologyDocument
from bson import ObjectId

async def find_ontology_by_id(ontology_id: str):
    onto_id = ObjectId(ontology_id)
    ontology_docu = await onto_collection.find_one({'_id': onto_id})
    
    if ontology_docu is not None:   
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)

        return ontology_document
    return None