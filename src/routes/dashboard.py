from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/dashboard/metrics")
async def get_dashboard_metrics():
    return JSONResponse(content={
        "totalLeads": 120,
        "convertedLeads": 48,
        "pipelineProgress": 72
    })
