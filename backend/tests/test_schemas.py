"""
Tests for Pydantic schemas
"""
import pytest
from app.models.schemas import (
    RedisMode,
    TaskStatus,
    LogLevel,
    RedisConfig,
    SyncTaskCreate,
    APIResponse
)


def test_redis_mode_enum():
    """Test RedisMode enum values"""
    assert RedisMode.STANDALONE == "standalone"
    assert RedisMode.SENTINEL == "sentinel"
    assert RedisMode.CLUSTER == "cluster"


def test_task_status_enum():
    """Test TaskStatus enum values"""
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.RUNNING == "running"
    assert TaskStatus.COMPLETED == "completed"
    assert TaskStatus.FAILED == "failed"
    assert TaskStatus.STOPPED == "stopped"


def test_log_level_enum():
    """Test LogLevel enum values"""
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"
    assert LogLevel.CRITICAL == "CRITICAL"


def test_redis_config_creation():
    """Test RedisConfig model creation"""
    config = RedisConfig(
        name="test-config",
        mode=RedisMode.STANDALONE,
        host="localhost",
        port=6379
    )
    assert config.name == "test-config"
    assert config.mode == RedisMode.STANDALONE
    assert config.host == "localhost"
    assert config.port == 6379
    assert config.database == 0  # default value


def test_redis_config_validation():
    """Test RedisConfig validation"""
    config = RedisConfig(
        name="test-config",
        mode=RedisMode.STANDALONE,
        host="localhost",
        port=6379
    )
    errors = config.validate_config()
    assert len(errors) == 0


def test_sync_task_create():
    """Test SyncTaskCreate model"""
    task = SyncTaskCreate(
        name="test-task",
        custom_config="[sync_reader]\naddress = \"localhost:6379\"\n[redis_writer]\naddress = \"localhost:6380\""
    )
    assert task.name == "test-task"
    assert "sync_reader" in task.custom_config
    assert "redis_writer" in task.custom_config


def test_api_response():
    """Test APIResponse model"""
    response = APIResponse(
        success=True,
        message="Test message",
        data={"key": "value"}
    )
    assert response.success is True
    assert response.message == "Test message"
    assert response.data == {"key": "value"}
