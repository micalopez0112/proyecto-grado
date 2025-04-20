from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SchemaCreateData:
    """Data for creating a schema."""
    json_schema: Dict[str, Any]
    collection_path: Optional[str] = None
    schema_id: Optional[str] = None

def clean_json_schema(json_schema: Dict[str, Any]):
    """Clean and normalize a JSON schema by handling null types and nested structures."""
    try:
        properties = json_schema.get("properties", {})
        for field_key, field_value in properties.items():
            entry_type = field_value.get("type")

            if isinstance(entry_type, list):
                entry_type = [x for x in entry_type if x != "null"]
                if entry_type:
                    field_value["type"] = entry_type[0]
                else:
                    print(f"No valid type found for field {field_key}")
            
            elif entry_type is None and field_value.get("anyOf") is not None:
                anyOf = field_value.get("anyOf")
                entry_type = [item for item in anyOf if item.get("type") != "null"]
                if entry_type:
                    properties[field_key] = entry_type[0]
                    if entry_type[0].get("type") == "object":
                        clean_json_schema(entry_type[0])
                    elif entry_type[0].get("type") == "array":
                        items_value = entry_type[0].get("items", {})
                        if isinstance(items_value, dict):
                            clean_json_schema(items_value)
            
            if field_value.get("type") == "object":
                clean_json_schema(field_value)
            elif field_value.get("type") == "array":
                items_value = field_value.get("items", {})
                if isinstance(items_value, dict):
                    clean_json_schema(items_value)

        return json_schema
    except Exception as e:
        print(f"Error cleaning schema: {e}")
        return None

def find_json_keys(path: str, json_key_separator: str = '?'):
    """Extract JSON keys from a mapping path."""
    keys = path.replace('-', json_key_separator).split(json_key_separator)
    json_keys = keys[:-1]
    if 'rootObject' in json_keys:
        json_keys.remove('rootObject')
    return json_keys

def find_element_in_json_instance(json_document: Dict[str, Any], path: str, json_key_separator: str = '?'):
    """Find an element in a JSON instance using a path."""
    keys = path.replace('-', json_key_separator).split(json_key_separator)
    json_keys = keys[:-1]
    if 'rootObject' in json_keys:
        json_keys.remove('rootObject')
    
    element = json_document
    try:
        for key in json_keys:
            element = element[key]
        return element
    except (KeyError, TypeError):
        return None
