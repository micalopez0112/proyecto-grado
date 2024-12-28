from fastapi import APIRouter
from fastapi import APIRouter, Query, Body
from typing import List,Optional, Dict, Any

from app.services import metadata_service
from app.models.mapping import  MappingResponse 
from app.dq_evaluation.evaluation import StrategyContext

router = APIRouter()


@router.post("/evaluate/{quality_rule}")
async def evaluate_quality(quality_rule: str, mapping_process_id: Optional[str] = Query(None, description="ID for mapping"), request_mapping_body: Dict[str, Any]= Body(...)):
    print(f'request_mapping_body: {request_mapping_body}')
    try :
        context = StrategyContext()
        context.select_strategy(quality_rule)
        
        result = await context.evaluate_quality(mapping_process_id, request_mapping_body)
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
    print(f'request_mapping_body: {request_mapping_body}')
    try :
        result = metadata_service.create_dq_model(mapping_process_id, request_mapping_body)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response