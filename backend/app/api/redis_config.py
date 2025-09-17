from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import (
    APIResponse,
    RedisConfigCreate,
    RedisConfigUpdate,
)
from app.services.redis_service import RedisService

router = APIRouter()


# Dependency injection
def get_redis_service():
    return RedisService()


@router.get("/configs", response_model=APIResponse)
async def get_redis_configs(service: RedisService = Depends(get_redis_service)):
    """Get all Redis configurations"""
    try:
        configs = await service.get_all_configs()
        return APIResponse(data=configs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs/{config_id}", response_model=APIResponse)
async def get_redis_config(
    config_id: str, service: RedisService = Depends(get_redis_service)
):
    """Get specific Redis configuration"""
    try:
        config = await service.get_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return APIResponse(data=config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configs", response_model=APIResponse)
async def create_redis_config(
    config: RedisConfigCreate, service: RedisService = Depends(get_redis_service)
):
    """Create Redis configuration

    Supports three Redis modes:
    1. standalone: Single instance mode
    2. sentinel: Sentinel mode (requires sentinel_hosts and master_name configuration)
    3. cluster: Cluster mode (requires cluster_nodes configuration)
    """
    try:
        created_config = await service.create_config(config)
        return APIResponse(
            data=created_config, message="Configuration created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/configs/{config_id}", response_model=APIResponse)
async def update_redis_config(
    config_id: str,
    config_update: RedisConfigUpdate,
    service: RedisService = Depends(get_redis_service),
):
    """UpdateRedisconfiguration"""
    try:
        updated_config = await service.update_config(config_id, config_update)
        if not updated_config:
            raise HTTPException(status_code=404, detail="configurationnot found")
        return APIResponse(
            data=updated_config, message="configurationUpdatesuccessfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/configs/{config_id}", response_model=APIResponse)
async def delete_redis_config(
    config_id: str, service: RedisService = Depends(get_redis_service)
):
    """DeleteRedisconfiguration"""
    try:
        success = await service.delete_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="configurationnot found")
        return APIResponse(message="configurationDeletesuccessfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configs/{config_id}/test", response_model=APIResponse)
async def test_redis_connection(
    config_id: str, service: RedisService = Depends(get_redis_service)
):
    """TestRedisconnection"""
    try:
        result = await service.test_connection(config_id)
        return APIResponse(data=result, message="Connection test completed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
