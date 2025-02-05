from fastapi import File, UploadFile, HTTPException, Form
from typing import Optional, List, Any
from app.models.ontology import OntologyDocument
from owlready2 import get_ontology, default_world, close_world, World
from app.repositories import ontology_repo
from app.rules_validation.utils import is_duplicate_ontology
import os
toDirectory = "upload/ontologies"


async def save_ontology(type: str = Form(...), ontology_file: Optional[UploadFile] = File(None), uri: Optional[str] = Form(None)):
    try:
        ontology_id = ''
        ontology_data = {}

        if ontology_file and type == "FILE":
            if not os.path.exists(toDirectory):
                os.makedirs(toDirectory)
            completePath = os.path.join(toDirectory, ontology_file.filename)
            completePath = completePath.replace(os.sep, '/')

            # Guardar el archivo en el servidor
            with open(completePath, "wb") as f:
                ontology_content = await ontology_file.read()
                f.write(ontology_content)

            # Cargar la ontología
            ontology = get_ontology(completePath).load()

            onto_in_collection = await ontology_repo.find_ontology_by_file_path(completePath)
            if not onto_in_collection:
                ontoDocu = OntologyDocument(type=type, file=completePath)
                inserted_id = await ontology_repo.insert_ontology(ontoDocu)
                ontology_id = inserted_id
            else:
                ontology_id = str(onto_in_collection.id)

        elif uri and type == "URI":
            # Cargar la ontología desde la URI
            ontology = get_ontology(uri).load()

            onto_in_collection = await ontology_repo.find_ontology_by_uri(uri)
            if not onto_in_collection:
                ontoDocu = OntologyDocument(type=type, uri=uri)
                inserted_id = await ontology_repo.insert_ontology(ontoDocu)
                ontology_id = inserted_id
            else:
                ontology_id = str(onto_in_collection.id)

        else:
            raise HTTPException(status_code=400, detail="No ontology FILE or URI provided")

        print("Ontología cargada correctamente. ID:", ontology_id)

        # Construir respuesta sin duplicados
        ontology_data = build_ontology_response(ontology, ontology_id)
        return ontology_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

async def get_ontology_by_id(ontology_id: str):
    ontology = await ontology_repo.find_ontology_by_id(ontology_id)
    if ontology is not None:
        if ontology.type == "FILE":
            ontology_iri = ontology.file
        else:
            ontology_iri = ontology.uri
        ontology = get_ontology(str(ontology_iri)).load()
    #ontology.imported_ontologies.append(get_ontology("http://www.w3.org/2000/01/rdf-schema"))
    return ontology

def build_ontology_response(ontology, onto_id):
    classes = list(ontology.classes())
    object_properties = list(ontology.object_properties())
    data_properties = list(ontology.data_properties())
    print("Ontology object properties:", object_properties)
    ##Provitional solution to avoid duplicate object properties
    seen_object_properties = set()
    # Usamos set para evitar duplicados
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

    #end of provitional solution
    
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
    
    
async def delete_ontology_by_id(ontology_id: str) -> bool:
    result = ontology_repo.delete_ontology_by_id(ontology_id)
    return result
  
