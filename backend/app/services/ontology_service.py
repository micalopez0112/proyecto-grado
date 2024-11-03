from app.repositories import ontology_repo
from owlready2 import get_ontology

async def get_ontology_by_id(ontology_id: str):
    ontology = await ontology_repo.find_ontology_by_id(ontology_id)
    if ontology is not None:
        if ontology.type == "FILE":
            ontology_path = ontology.file
            ontology = get_ontology(ontology_path).load()
        else:
            ontology = get_ontology(str(ontology.uri)).load()
   
    return ontology