from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import APIResponse, SyncTask, SyncTaskCreate, SyncTaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


# Dependency injection
def get_task_service():
    return TaskService()


@router.get("/", response_model=APIResponse)
async def get_sync_tasks(service: TaskService = Depends(get_task_service)):
    """Get all sync tasks"""
    try:
        tasks = await service.get_all_tasks()
        return APIResponse(data=tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=APIResponse)
async def get_sync_task(task_id: str, service: TaskService = Depends(get_task_service)):
    """Get specific sync task"""
    try:
        task = await service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return APIResponse(data=task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=APIResponse)
async def create_sync_task(
    task: SyncTaskCreate, service: TaskService = Depends(get_task_service)
):
    """Create sync task

    Note: Must provide custom TOML configuration content (custom_config field), otherwise the task cannot start.
    Configuration content should contain complete redis-shake configuration, for example:

    ```toml
    [sync_reader]
    address = "127.0.0.1:6379"
    password = ""

    [redis_writer]
    address = "127.0.0.1:6380"
    password = ""

    [filter]
    allow_keys = []

    [advanced]
    log_file = "shake.log"
    ```
    """
    try:
        # Validate if custom configuration is provided
        if not task.custom_config:
            raise HTTPException(status_code=400, detail="Must provide custom TOML configuration content")

        created_task = await service.create_task(task)
        return APIResponse(data=created_task, message="Task created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}", response_model=APIResponse)
async def update_sync_task(
    task_id: str,
    task_update: SyncTaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """Update sync task"""
    try:
        updated_task = await service.update_task(task_id, task_update)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return APIResponse(data=updated_task, message="Task updated successfully")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", response_model=APIResponse)
async def delete_sync_task(
    task_id: str, service: TaskService = Depends(get_task_service)
):
    """Delete sync task

    Note: Only non-running tasks can be deleted.
    If the task is running, you must first call the stop task interface and wait for the task to stop before deleting.

    Deleting a task will also clean up related configuration files.
    """
    try:
        success = await service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return APIResponse(message="Task deleted successfully")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/start", response_model=APIResponse)
async def start_sync_task(
    task_id: str, service: TaskService = Depends(get_task_service)
):
    """Start sync task"""
    try:
        result = await service.start_task(task_id)
        return APIResponse(data=result, message="Task start command sent")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/stop", response_model=APIResponse)
async def stop_sync_task(
    task_id: str, service: TaskService = Depends(get_task_service)
):
    """Stop sync task"""
    try:
        result = await service.stop_task(task_id)
        return APIResponse(data=result, message="Task stop command sent")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/status", response_model=APIResponse)
async def get_task_status(
    task_id: str, service: TaskService = Depends(get_task_service)
):
    """Get task real-time status"""
    try:
        status_info = await service.get_task_status(task_id)
        return APIResponse(data=status_info, message="Task status retrieved successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/realtime-status", response_model=APIResponse)
async def get_task_realtime_status(
    task_id: str, service: TaskService = Depends(get_task_service)
):
    """Get task Redis-Shake real-time status"""
    try:
        realtime_status = await service.get_realtime_status(task_id)
        return APIResponse(data=realtime_status, message="Real-time status retrieved successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/overview", response_model=APIResponse)
async def get_tasks_statistics(service: TaskService = Depends(get_task_service)):
    """Get task statistics"""
    try:
        statistics = await service.get_tasks_statistics()
        return APIResponse(data=statistics, message="Statistics retrieved successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
