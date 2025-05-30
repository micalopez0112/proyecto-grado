from fastapi import APIRouter, Query, Body, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, Annotated

from app.services.metadata.service import MetadataService
from app.models.mapping import MappingResponse
from app.dq_evaluation.evaluation import StrategyContext
from app.dependencies import get_metadata_service, get_metadata_repository
from app.services.metadata.types import CreateDQModelRequest, GetEvaluationResultsRequest
from ..database import neo4j_conn
from app.repositories.metadata.repository import MetadataRepository

import time

router = APIRouter()

class ConnectionCredentials(BaseModel):
    uri: str
    user: str
    password: str

@router.post("/update-neo4j-connection")
async def update_neo4j_connection(metadata_repo: Annotated[MetadataRepository, Depends(get_metadata_repository)], request: ConnectionCredentials = Body(...)):
    # CAMBIAR PARAMETROS A BODY
    try:
        uri = request.uri
        user = request.user
        password = request.password
        print("Credentials: " + uri + " " + user + " " + password)
        if(uri == "" and user == "" and password == ""):
            print("Credentials are empty")
            neo4j_conn.re_connect_local();
        else:
            external_driver = neo4j_conn.connect(uri, user, password)
            metadata_repo.set_neo4j_driver(external_driver)
            metadata_repo.init_governance_zone();
            # pasar todo a service
        print("Neo4j connection updated successfully, and the governance_zone initialized")
        return {"message": "Neo4j connection updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update connection: {str(e)}")


@router.post("/evaluate/{quality_rule}")
async def evaluate_quality(
    metadata_service: Annotated[MetadataService, Depends(get_metadata_service)],
    quality_rule: str,
    aggregation: str,
    dq_model_id: Optional[str] = Query(None, description="ID for mapping"),
    request_mapping_body: Dict[str, Any]= Body(...)
):
    try:
        context = StrategyContext()
        context.select_strategy(quality_rule, aggregation, metadata_service)
        inicio = time.time()
        result = await context.evaluate_quality(dq_model_id)
        fin = time.time()
        print(f"Tiempo de ejecución de la evaluación del dq_model_id: {dq_model_id} fue:-- {fin - inicio} --")
        return result
    except Exception as e:
        return MappingResponse(message=str(e), status="error")
        

@router.get("/results")
async def get_quality_results(
    metadata_service: Annotated[MetadataService, Depends(get_metadata_service)],
    mapping_process_id: Optional[str] = Query(None, description="ID for mapping"),
    dq_model_id: Optional[str] = Query(None, description="DQ Model ID"),
    json_key: Optional[str] = Query(None, description="Json key to get quality results"),
    limit: Optional[int] = 10,
    offset: Optional[int] = 0
):
    try:

        params = GetEvaluationResultsRequest(
            dq_model_id=dq_model_id,
            mapping_process_id=mapping_process_id,
            json_key=json_key,
            limit=limit,
            offset=offset
        )
        result, total = await metadata_service.get_evaluation_results_by_json(params)
        return {"results": result, "total": total}
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response


@router.post("/model")
async def create_dq_model(
    metadata_service: Annotated[MetadataService, Depends(get_metadata_service)],
    request_mapping_body: Dict[str, Any] = Body(...),
    mapping_process_id: Optional[str] = Query(None, description="ID for mapping"),
    dq_model_name: Optional[str] = Query(None, description="DQ model name"),
    dq_method_id: Optional[str] = Query(None, description="DQ method id"),
    dq_aggregated_method_id: Optional[str] = Query(None, description="DQ aggregated method id")
): 
    try:
        create_params = CreateDQModelRequest(
            mapping_process_id=mapping_process_id,
            dq_model_name=dq_model_name,
            dq_method_id=dq_method_id,
            dq_aggregated_method_id=dq_aggregated_method_id,
            mapped_entries=list(request_mapping_body.keys())
        )
        result = await metadata_service.create_dq_model(create_params, request_mapping_body)
        return result
    except Exception as e:
        print("### Error creating DQ model ###", str(e))
        return MappingResponse(message=str(e), status="error")

@router.get("/models")
async def get_dq_models(
    metadata_service: Annotated[MetadataService, Depends(get_metadata_service)],
    mapping_process_id: str = Query(None, description="ID for mapping"),
    quality_method_id: str = Query(None, description="ID for quality rule")
):
    try:
        result = await metadata_service.get_dq_models(mapping_process_id, quality_method_id)
        return result
    except Exception as e:
        return MappingResponse(message= str(e), status="error")


@router.get("/applied_methods")
async def get_applied_methods(
    metadata_service: Annotated[MetadataService, Depends(get_metadata_service)],
    dq_model_id: str = Query(None, description="DQ Model id")
):
    try:
        result = await metadata_service.get_applied_methods_by_dq_model(dq_model_id)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
    
@router.get("/data-quality-rules")
async def get_data_quality_rules(
    metadata_service: Annotated[MetadataService, Depends(get_metadata_service)]
):
    try:
        result = await metadata_service.get_data_quality_rules()
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
        
# TODO: posible pero no se si quda aca. Me parece que esto ya no
# @router.get("/metrics")
# async def get_metrics():
#     try :
#         result = await metadata_service.get_applied_methods_by_dq_model(dq_model_id)
#         return result
#     except Exception as e:
#         msg = str(e)
#         response = MappingResponse(message=msg, status="error")
#         return response