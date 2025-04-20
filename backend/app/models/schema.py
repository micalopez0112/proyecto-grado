

from pydantic import BaseModel,Field,HttpUrl
from typing import Dict, Any, Optional, List
from bson import ObjectId

class JsonSchema(BaseModel):
    id : Optional[ObjectId] = Field(alias="_id") 
    collection_name : str = None
    schema: str = Field(alias="$schema")
    type: str 
    properties: Dict[str, Any]
    # { "destinp": { "type": "object", "properties": {}} }
    required: Optional[List[str]] = None

    def __init__(self, **data):
        super().__init__(**data) 
    # property_name = 
    class Config:
        arbitrary_types_allowed = True  # Permitir tipos arbitrarios como ObjectId
        json_encoders = {
            ObjectId: str  # Convertir ObjectId a string al serializar
        }

    def findPropertyInJsonSchema(self, property_name: str)-> Optional[Dict[str, Any]]:
        print("## PROPERTY NAME: ##", property_name)
        properties = property_name.split("?")[0]
        properties_names = properties.split("-")
        properties_names = properties_names[1:]
        current_level = self.properties
        print("##Current level: ##", current_level)
        if len(properties_names) == 1:
            looked_prop = properties_names[0]
            if looked_prop in current_level:
                return current_level[looked_prop]
            else:
                return None
   
        current_level = self.properties[properties_names[0]]
        properties_names = properties_names[1:]
        for prop_name in properties_names:
            print("##PropName: ##", prop_name)
            print("## CURRENT LEVEL: ##", current_level)
            if 'properties' in current_level and prop_name in current_level['properties']:
                print("### PROPERTY NAME: ##", prop_name)
                current_level = current_level['properties'][prop_name]
                print("## CURRENT PROP: ##", current_level)
            elif 'items' in current_level:
                item = current_level['items']
                print("## ITEMS: ##", item)
                if 'properties' in item and prop_name in item['properties']:
                        current_level = item['properties'][prop_name]
                else:
                    return None
                # for item in items:
                #     print("## ITEM PROPERTIES: ##", item['properties'])
                    
            else:
                return None
        return current_level
    
class JSONSchemaResponse(BaseModel):
    id : Optional[str] = None
    collection_name : str = None
    properties : Optional [Dict[str, Any]] = None
    is_external : Optional [bool] = None

class JsonRequestList(BaseModel):
    jsonInstances: List[dict] 