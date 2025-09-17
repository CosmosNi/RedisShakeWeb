from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.schemas import APIResponse, TaskLogCreate
from app.services.log_service import LogService

router = APIRouter()


# Dependency injection
def get_log_service():
    return LogService()


@router.get("/", response_model=APIResponse)
async def get_all_logs(
    limit: int = Query(100, description="Log count limit"),
    level: Optional[str] = Query(None, description="Log level filter"),
    task_id: Optional[str] = Query(None, description="Task ID filter"),
    service: LogService = Depends(get_log_service),
):
    """Get all task logs"""
    try:
        logs = service.get_all_logs(limit=limit, level=level, task_id=task_id)
        return APIResponse(data=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=APIResponse)
async def get_task_logs(
    task_id: str,
    limit: int = Query(100, description="Log count limit"),
    level: Optional[str] = Query(None, description="Log level filter"),
    service: LogService = Depends(get_log_service),
):
    """Get specifictask"""
    try:
        logs = service.get_logs_by_task(task_id, limit=limit, level=level)
        return APIResponse(data=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=APIResponse)
async def add_log(
    log_create: TaskLogCreate, service: LogService = Depends(get_log_service)
):
    """Add task log"""
    try:
        log = service.add_log(log_create)
        return APIResponse(data=log, message="successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=APIResponse)
async def search_logs(
    keyword: str = Query(..., description="Search keyword"),
    limit: int = Query(100, description="Log count limit"),
    service: LogService = Depends(get_log_service),
):
    """"""
    try:
        logs = service.search_logs(keyword, limit)
        return APIResponse(data=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/task/{task_id}", response_model=APIResponse)
async def clear_task_logs(task_id: str, service: LogService = Depends(get_log_service)):
    """Clear logs for specified task"""
    try:
        success = service.clear_logs_by_task(task_id)
        if success:
            return APIResponse(message="tasksuccessfully")
        else:
            raise HTTPException(status_code=500, detail="failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/", response_model=APIResponse)
async def clear_all_logs(service: LogService = Depends(get_log_service)):
    """"""
    try:
        success = service.clear_all_logs()
        if success:
            return APIResponse(message="successfully")
        else:
            raise HTTPException(status_code=500, detail="failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
