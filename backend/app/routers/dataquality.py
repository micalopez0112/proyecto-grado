from fastapi import APIRouter, Query, Body, HTTPException
from typing import List,Optional, Dict, Any

from app.services import metadata_service
from app.models.mapping import  MappingResponse,  DQModel
from app.dq_evaluation.evaluation import StrategyContext
from ..database import neo4j_conn

from app.repositories import metadata_repo

router = APIRouter()


@router.post("/update-neo4j-connection")
async def update_neo4j_connection(uri: str, user: str, password: str):
    try:
        print("Credentials: " + uri + " " + user + " " + password)
        neo4j_conn.connect(uri, user, password)
        print("Neo4j connection updated successfully, just before execute_test_query")
        return {"message": "Neo4j connection updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update connection: {str(e)}")

@router.post("/execute-test-query")
async def execute_tq():
    try:
        result = metadata_repo.execute_test_query()
        print("RESULT en ENDPOINT: ", result)
        return {"message": "Test query executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute test query: {str(e)}")

@router.post("/evaluate/{quality_rule}")
async def evaluate_quality(quality_rule: str, dq_model_id: Optional[str] = Query(None, description="ID for mapping"), request_mapping_body: Dict[str, Any]= Body(...)):
    print(f'request_mapping_body: {request_mapping_body}')
    try :
        context = StrategyContext()
        context.select_strategy(quality_rule)
        
        result = await context.evaluate_quality(dq_model_id)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
        

@router.get("/results")
async def get_quality_results(mapping_process_id: Optional[str] = Query(None, description="ID for mapping"), 
                              json_key: Optional[str] = Query(None, description="Json key to get quality results, its the mapping key"), 
                              limit: Optional[int] = 100, offset: Optional[int] = 0):
    print(f'request_mapping_body: {mapping_process_id}')
    try :
        result = await metadata_service.get_evaluation_results_by_json(mapping_process_id, json_key, limit, offset)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
        
@router.post("/model")
async def create_dq_model(mapping_process_id: Optional[str] = Query(None, description="ID for mapping"), request_mapping_body: Dict[str, Any]= Body(...)):
    print("### Starting create DQ model process ###")
    print(f'request_mapping_body: {request_mapping_body}')
    try :
        result = await metadata_service.create_dq_model(mapping_process_id, request_mapping_body)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response

@router.get("/models")
async def get_dq_models(mapping_process_id: str = Query(None, description="ID for mapping"), quality_method_id: str = Query(None, description="ID for quality rule")):
    try :
        result = await metadata_service.get_dq_models(mapping_process_id,quality_method_id)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response


@router.get("/applied_methods")
async def get_quality_results(dq_model_id: str = Query(None, description="DQ Model id")):
    try :
        result = await metadata_service.get_applied_methods_by_dq_model(dq_model_id)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
        