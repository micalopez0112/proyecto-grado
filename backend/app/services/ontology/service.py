import os
from owlready2 import get_ontology
from app.repositories.ontology.repository import OntologyRepository
from app.models.ontology import OntologyDocument
from .exceptions import OntologyNotFoundError, InvalidOntologyDataError
from .types import OntologyCreateData, build_ontology_response

class OntologyService:
    def __init__(self, ontology_repository: OntologyRepository):
        self.repository = ontology_repository
        self.upload_directory = "upload/ontologies"

    async def save(self, ontology_data: OntologyCreateData):
        """
        Save an ontology from a file or URI.
        Returns the ontology data and ID.
        """
        try:
            ontology_id = ''
            ontology = None

            if ontology_data.type == "FILE" and ontology_data.file_path:
                if not os.path.exists(self.upload_directory):
                    os.makedirs(self.upload_directory)
                
                complete_path = os.path.join(self.upload_directory, os.path.basename(ontology_data.file_path))
                complete_path = complete_path.replace(os.sep, '/')

                onto_in_collection = await self.repository.find_ontology_by_file_path(complete_path)
                if not onto_in_collection:
                    onto_doc = OntologyDocument(type=ontology_data.type, file=complete_path)
                    ontology_id = await self.repository.insert_ontology(onto_doc)
                else:
                    ontology_id = str(onto_in_collection.id)

                ontology = get_ontology(complete_path).load()

            elif ontology_data.type == "URI" and ontology_data.uri:
                onto_in_collection = await self.repository.find_ontology_by_uri(ontology_data.uri)
                if not onto_in_collection:
                    onto_doc = OntologyDocument(type=ontology_data.type, uri=ontology_data.uri)
                    ontology_id = await self.repository.insert_ontology(onto_doc)
                else:
                    ontology_id = str(onto_in_collection.id)

                ontology = get_ontology(ontology_data.uri).load()
            else:
                raise InvalidOntologyDataError("No valid ontology FILE or URI provided")

            if not ontology:
                raise InvalidOntologyDataError("Failed to load ontology")

            return build_ontology_response(ontology, ontology_id)

        except Exception as e:
            raise InvalidOntologyDataError(f"Could not save ontology: {str(e)}")

    async def get_ontology_by_id(self, ontology_id: str):
        """
        Get an ontology by its ID.
        Returns the loaded ontology object.
        """
        ontology_doc = await self.repository.find_ontology_by_id(ontology_id)
        if ontology_doc is None:
            raise OntologyNotFoundError(f"Ontology {ontology_id} not found")

        ontology_iri = ontology_doc.file if ontology_doc.type == "FILE" else ontology_doc.uri
        return get_ontology(str(ontology_iri)).load()

    async def delete_ontology_by_id(self, ontology_id: str):
        """
        Delete an ontology by its ID.
        Returns True if successful.
        """
        result = await self.repository.delete_ontology_by_id(ontology_id)
        if not result:
            raise OntologyNotFoundError(f"Ontology {ontology_id} not found")
        return True