from fastapi import File, UploadFile, HTTPException, Form
from typing import Optional, List, Any
from app.models.ontology import OntologyDocument
from owlready2 import get_ontology
from app.repositories import ontology_repo
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
            print("os sep: ", os.sep)
            completePath = completePath.replace(os.sep, '/')
            print("onto path", completePath)
            onto_in_collection = await ontology_repo.find_ontology_by_file_path(completePath)
            #check if the file already exists (search by completePath)
            # ontology.imported_ontologies.append(get_ontology("http://www.w3.org/2000/01/rdf-schema"))
            if not onto_in_collection:
                print("onto not in collection")
                with open(completePath, "wb") as f:
                    ontology_content = await ontology_file.read()
                    f.write(ontology_content)
                ontoDocu = OntologyDocument(type=type, file=completePath)
            else:
                print("onto in collection")
                ontology_id = str(onto_in_collection.id)
            ontology = get_ontology(completePath).load()
            print("Onto loaded")
        elif uri and type == "URI":
         # Manejo de la URI
            print("onto uri", uri)
            #check if the file already exists (search by uri)
            onto_in_collection = await ontology_repo.find_ontology_by_uri(uri)
            if not onto_in_collection:
                print("onto not in collection")
                ontoDocu = OntologyDocument(type=type, uri=uri)
            else:
                ontology_id = str(onto_in_collection.id)
            ontology = get_ontology(str(uri)).load()
        else:
            raise HTTPException(status_code=400, detail="No ontology FILE or URI provided")
        if(ontology_id == ''):
            inserted_id = await ontology_repo.insert_ontology(ontoDocu)
            ontology_id = inserted_id
            print("Inserted correctly - Ontology ID:", ontology_id)
        else:
            print("Ontology already exists - Ontology ID:", ontology_id)
        ontology_data = build_ontology_response(ontology, ontology_id)
        print("##return de la ontologia al hacer el upload (ver si hay object properties repetidas)##", ontology_data)
        return ontology_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

async def get_ontology_by_id(ontology_id: str):
    ontology = await ontology_repo.find_ontology_by_id(ontology_id)
    if ontology is not None:
        if ontology.type == "FILE":
            ontology_path = ontology.file
            ontology = get_ontology(ontology_path).load()
        else:
            ontology = get_ontology(str(ontology.uri)).load()
    ontology.imported_ontologies.append(get_ontology("http://www.w3.org/2000/01/rdf-schema"))

    return ontology

def build_ontology_response(ontology, onto_id):
    classes = list(ontology.classes())
    object_properties = list(ontology.object_properties())
    data_properties = list(ontology.data_properties())
    print("Ontology object properties:", object_properties)
    for prop in object_properties:
        print("Object property ("+prop.name+") range: "+ str(prop.range))
    return {
        "ontology_id": onto_id,
        "ontoData": [{
            "data": [{
                "classes": [{"name": cls.name, "iri": cls.iri} for cls in classes],
                "object_properties": [{"name": prop.name, "iri": prop.iri,"range":{"name":range.name,"iri":range.iri}} for prop in object_properties for range in prop.range],
                "data_properties": [{"name": prop.name, "iri": prop.iri} for prop in data_properties]
            }]
        }]
    }
    
    
async def delete_ontology_by_id(ontology_id: str) -> bool:
    result = ontology_repo.delete_ontology_by_id(ontology_id)
    return result
  
