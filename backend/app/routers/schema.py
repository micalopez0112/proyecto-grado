from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.services.schema.service import SchemaService
from app.dependencies import get_schema_service

router = APIRouter()


@router.get("/")
async def get_schemas(
    schema_service: Annotated[SchemaService, Depends(get_schema_service)]
): 
    schemas = await schema_service.get_all_schemas()
    return schemas

@router.get("/generateSchema")
async def get_schema_from_path(
    collectionPath: str,
    schema_service: Annotated[SchemaService, Depends(get_schema_service)]
):
    try:
        schema = schema_service.generate_schema_from_collection(collectionPath)
        if(schema):
            print(f'## SCHEMA al retornar en generateSchema ##: {schema}')
            return schema
        else:
            raise HTTPException(status_code=500, detail="Error al generar el esquema")
    except Exception as e:
        print(f"Error al generar el esquema: {e}")
        raise HTTPException(status_code=500, detail=str(e))