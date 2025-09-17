import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

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


@router.get("/task/{task_id}/stream")
async def stream_task_logs(
    task_id: str, service: LogService = Depends(get_log_service)
):
    """Stream real-time task logs using Server-Sent Events"""

    async def event_generator():
        """Generate SSE events for task logs"""
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to log stream'})}\n\n"

            # Get existing logs first
            existing_logs = service.get_logs_by_task(task_id, limit=50)
            for log in existing_logs:
                log_data = {
                    "type": "log",
                    "timestamp": log.timestamp,
                    "level": log.level,
                    "message": log.message,
                    "task_id": log.task_id,
                }
                yield f"data: {json.dumps(log_data)}\n\n"

            # Stream new logs in real-time
            last_check = len(existing_logs)
            while True:
                try:
                    # Get new logs since last check
                    all_logs = service.get_logs_by_task(task_id, limit=100)
                    new_logs = all_logs[last_check:]

                    for log in new_logs:
                        log_data = {
                            "type": "log",
                            "timestamp": log.timestamp,
                            "level": log.level,
                            "message": log.message,
                            "task_id": log.task_id,
                        }
                        yield f"data: {json.dumps(log_data)}\n\n"

                    last_check = len(all_logs)

                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': str(asyncio.get_event_loop().time())})}\n\n"

                    # Wait before next check
                    await asyncio.sleep(1)

                except asyncio.CancelledError:
                    # Client disconnected
                    yield f"data: {json.dumps({'type': 'disconnected', 'message': 'Stream disconnected'})}\n\n"
                    break
                except Exception as e:
                    # Send error event
                    error_data = {
                        "type": "error",
                        "message": f"Stream error: {str(e)}",
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    await asyncio.sleep(5)  # Wait before retry

        except Exception as e:
            # Send final error event
            error_data = {"type": "error", "message": f"Fatal stream error: {str(e)}"}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )
