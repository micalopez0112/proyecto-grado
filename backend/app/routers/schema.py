
from fastapi import APIRouter, HTTPException
from app.services import schema_service as service

router = APIRouter()


@router.get("/")
async def get_schemas(): 
    schemas = await service.get_all_schemas()
    return schemas

@router.get("/generateSchema")
async def get_schema_from_path(collectionFileName: str):
    try:
        schema = service.generate_schema_from_collection(collectionFileName)
        print(f'## SCHEMA al retornar en generateSchema ##: {schema}')
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))