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

def build_ontology_response(ontology, onto_id):
    classes = list(ontology.classes())
    object_properties = list(ontology.object_properties())
    data_properties = list(ontology.data_properties())
    ontology_data = {
        "ontology_id": onto_id,
        "ontoData": [{
            "data": [{
                "classes": [{"name": cls.name, "iri": cls.iri} for cls in classes],
                "object_properties": [{"name": prop.name, "iri": prop.iri,"range":{"name":range.name,"iri":range.iri}} for prop in object_properties for range in prop.range],
                "data_properties": [{"name": prop.name, "iri": prop.iri} for prop in data_properties]
            }]
        }]
    }