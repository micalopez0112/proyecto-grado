from dataclasses import dataclass
from typing import Optional

@dataclass
class OntologyCreateData:
    type: str
    file_path: Optional[str] = None
    uri: Optional[str] = None

def build_ontology_response(ontology, onto_id):
    """Build a standardized response for ontology data."""
    classes = list(ontology.classes())
    object_properties = list(ontology.object_properties())
    data_properties = list(ontology.data_properties())
    
    # Avoid duplicate object properties using a set
    seen_object_properties = set()
    response_object_properties = []
    
    for prop in object_properties:
        for range in prop.range:
            key = (prop.name, prop.iri, range.name, range.iri)
            if key not in seen_object_properties:
                seen_object_properties.add(key)
                response_object_properties.append({
                    "name": prop.name,
                    "iri": prop.iri,
                    "range": {
                        "name": range.name,
                        "iri": range.iri
                    }
                })
    
    return {
        "ontology_id": onto_id,
        "ontoData": [{
            "data": [{
                "classes": [{"name": cls.name, "iri": cls.iri} for cls in classes],
                "object_properties": response_object_properties,
                "data_properties": [{"name": prop.name, "iri": prop.iri} for prop in data_properties]
            }]
        }]
    }
