from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class MappingFilters(BaseModel):
    """Filters for mapping searches."""
    schema_id: Optional[str] = None
    validated: Optional[bool] = None
