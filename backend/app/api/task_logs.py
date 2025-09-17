import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.schemas import APIResponse, TaskLogCreate
from app.services.log_service import LogService
from app.services.task_service import TaskService

router = APIRouter()


# Dependency injection
def get_log_service():
    return LogService()

def get_task_service():
    return TaskService()


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
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    """Stream real-time Redis-Shake process logs using Server-Sent Events"""

    async def event_generator():
        """Generate SSE events for Redis-Shake process logs"""
        log_queue = asyncio.Queue()

        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to Redis-Shake log stream'})}\n\n"

            # Subscribe to task logs
            task_service.subscribe_to_logs(task_id, log_queue)

            # Check if task is running
            task = await task_service.get_task(task_id)
            if not task:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Task not found'})}\n\n"
                return

            if task.status != 'running':
                yield f"data: {json.dumps({'type': 'info', 'message': f'Task is {task.status}. Start the task to see real-time logs.'})}\n\n"
                # Still continue to listen in case task gets started

            # Stream logs in real-time
            heartbeat_counter = 0
            while True:
                try:
                    # Wait for log with timeout for heartbeat
                    try:
                        log_line = await asyncio.wait_for(log_queue.get(), timeout=5.0)

                        # Send log event
                        log_data = {
                            "type": "log",
                            "timestamp": log_line["timestamp"],
                            "level": log_line["level"],
                            "message": log_line["message"],
                            "source": log_line.get("source", "redis-shake"),
                            "task_id": task_id,
                        }
                        yield f"data: {json.dumps(log_data)}\n\n"

                    except asyncio.TimeoutError:
                        # Send heartbeat every 5 seconds if no logs
                        heartbeat_counter += 1
                        heartbeat_data = {
                            "type": "heartbeat",
                            "timestamp": str(asyncio.get_event_loop().time()),
                            "count": heartbeat_counter
                        }
                        yield f"data: {json.dumps(heartbeat_data)}\n\n"

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
        finally:
            # Clean up subscription
            try:
                task_service.unsubscribe_from_logs(task_id, log_queue)
            except Exception:
                pass

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
