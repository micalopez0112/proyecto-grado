from bson import ObjectId
from app.database import onto_collection
from app.models.ontology import OntologyDocument
from app.repositories.metadata.repository import MetadataRepository

class OntologyRepository:
    def __init__(self, collection=onto_collection, metadata_repo: MetadataRepository = None):
        self.collection = collection
        self.metadata_repo = metadata_repo

    async def find_by_id(self, ontology_id: str):
        """Find an ontology by its ID."""
        onto_id = ObjectId(ontology_id)
        ontology_doc = await self.collection.find_one({'_id': onto_id})
        
        if ontology_doc is not None:   
            ontology_doc['id'] = str(ontology_doc['_id'])
            return OntologyDocument(**ontology_doc)
        return None

    async def find_ontology_by_file_path(self, ontology_path: str):
        """Find an ontology by its file path."""
        ontology_doc = await self.collection.find_one({'file': ontology_path})
        if ontology_doc is not None:   
            ontology_doc['id'] = str(ontology_doc['_id'])
            return OntologyDocument(**ontology_doc)
        return None

    async def find_ontology_by_uri(self, uri: str):
        """Find an ontology by its URI."""
        ontology_doc = await self.collection.find_one({'uri': uri})
        if ontology_doc is not None:   
            ontology_doc['id'] = str(ontology_doc['_id'])
            return OntologyDocument(**ontology_doc)
        return None

    async def insert_ontology(self, ontology_document: OntologyDocument):
        """Insert a new ontology document."""
        onto_model_data = ontology_document.model_dump()
        if onto_model_data.get('uri'):
            onto_model_data['uri'] = str(onto_model_data['uri'])
            onto_name = onto_model_data['uri']
        else:
            onto_name = onto_model_data['file'].split('/')[-1]
        
        result = await self.collection.insert_one(onto_model_data)
        inserted_onto_id = str(result.inserted_id)
        self.metadata_repo.insert_context_metadata(inserted_onto_id, onto_name)
        return inserted_onto_id

    async def delete_ontology_by_id(self, ontology_id: str) -> bool:
        """Delete an ontology by its ID."""
        ontology_object_id = ObjectId(ontology_id)
        result = await self.collection.delete_one({"_id": ontology_object_id})
        return result.deleted_count > 0
