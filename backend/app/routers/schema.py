
from fastapi import APIRouter, HTTPException

from app.services import schema_service as service

router = APIRouter()


@router.get("/")
async def get_schemas(): 
    schemas = await service.get_all_schemas()
    return schemas

@router.get("/generateSchema")
async def get_schema_from_path(collectionPath: str):
    try:
        schema = service.generate_schema_from_collection(collectionPath)
        if(schema):
            return schema
        else:
            raise HTTPException(status_code=500, detail="Error al generar el esquema")
    except Exception as e:
        print(f"Error al generar el esquema: {e}")
        raise HTTPException(status_code=500, detail=str(e))