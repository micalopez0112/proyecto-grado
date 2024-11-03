
from fastapi import APIRouter
from app.services import schema_service as service
router = APIRouter()


@router.get("/")
async def get_schemas(): 
    schemas = await service.get_all_schemas()
    return schemas