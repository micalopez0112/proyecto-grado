

from pydantic import BaseModel,Field,HttpUrl
from typing import Dict, Any, Optional, List
from bson import ObjectId

class JsonSchema(BaseModel):
    id : Optional[str] = None
    collection_name : str = None
    schema: str = Field(alias="$schema")
    type: str 
    properties: Dict[str, Any]
    # { "destinp": { "type": "object", "properties": {}} }
    required: Optional[List[str]] = None
    # property_name = 
    def get_id(self):
        return str(self._id)
    
    def findPropertyInJsonSchema(self, property_name: str)-> Optional[Dict[str, Any]]:
        properties = property_name.split("_")[0]
        properties_names = properties.split("-")
        current_level = self.properties
        if len(properties_names) == 1:
            if property_name in current_level:
                return current_level[property_name]
            else:
                return None
   
        print("looking for property!")
        current_level = self.properties[properties_names[0]]
        properties_names = properties_names[1:]
        for prop_name in properties_names:
            if 'properties' in current_level and prop_name in current_level['properties']:
                print("### PROPERTY NAME: ##", prop_name)
                current_level = current_level['properties'][prop_name]
                print("## CURRENT PROP: ##", current_level)
            elif 'items' in current_level:
                items = current_level['items']
                print("## ITEMS: ##", items)
                for item in items:
                    print("## ITEM PROPERTIES: ##", item['properties'])
                    if 'properties' in item and prop_name in item['properties']:
                        current_level = item['properties'][prop_name]
                    else:
                        return None
            else:
                return None
        return current_level
    
class JSONSchemaResponse(BaseModel):
    id : Optional[str] = None
    collection_name : str = None
    properties : Optional[Dict[str, Any]] = None