import json
from genson import SchemaBuilder

from app.repositories.schema.repository import SchemaRepository
from app.repositories.metadata.repository import MetadataRepository
from app.models.schema import JSONSchemaResponse, JsonRequestList
from app.repositories.build_movies_metadata import generate_metadata_from_schema
from .types import SchemaCreateData, clean_json_schema
class SchemaService:
    def __init__(self, schema_repository: SchemaRepository, metadata_repository: MetadataRepository):
        self.repository = schema_repository
        self.metadata_repository = metadata_repository

    async def get_all_schemas(self):
        """Get all schemas."""
        schemas = await self.repository.find_all()
        result = []
        for schema in schemas:
            collection_name = schema.get('collection_name', "some_collection")
            is_external = schema.get('is_external', False)
            json_schema = JSONSchemaResponse(
                id=str(schema['_id']),
                collection_name=collection_name,
                is_external=is_external
            )
            result.append(json_schema)
        return result

    async def get_schema_by_id(self, schema_id: str):
        """Get a schema by its ID."""
        return await self.repository.find_by_id(schema_id)

    async def insert_schema(self, schema_data: SchemaCreateData):
        """Insert a new schema."""
        return await self.repository.insert(schema_data.json_schema, schema_data.schema_id)

    async def find_schema_by_collection_name(self, collection_name: str):
        """Find a schema by collection name."""
        return await self.repository.find_one_by_query({'collection_name': collection_name})

    async def get_or_create_schema(self, schema_data: SchemaCreateData):
        """Get an existing schema or create a new one."""
        collection_name = schema_data.json_schema.get('collection_name')
        if not collection_name:
            raise ValueError("JSON schema must have a collection_name")

        existing_schema = await self.find_schema_by_collection_name(collection_name)
        if existing_schema is None:
            schema_id = await self.insert_schema(schema_data)
            if schema_data.collection_path:
                self.metadata_repository.generate_metadata_from_schema(
                    schema_data.collection_path, 
                    schema_data.json_schema, 
                    str(schema_id)
                )
            return schema_id
        
        return existing_schema.id

    def generate_schema_from_collection(self, collection_file_path: str):
        """Generate a JSON schema from a collection file."""
        try:
            if not collection_file_path.endswith('.json'):
                print("File does not have .json extension")
                return None

            with open(collection_file_path, "r", encoding='utf-8') as file:
                builder = SchemaBuilder()
                file_content = json.load(file)
                json_data = JsonRequestList(jsonInstances=file_content)
                
                for json_obj in json_data.jsonInstances:
                    builder.add_object(json_obj)
                
                schema = builder.to_schema()
                return clean_json_schema(schema)

        except OSError as e:
            print("Error reading collection file:", e)
        except json.JSONDecodeError as e:
            print("Error decoding JSON file:", e)
        
        return None

    async def delete_schema_by_id(self, schema_id: str):
        """Delete a schema by its ID."""
        return await self.repository.delete_by_id(schema_id)
