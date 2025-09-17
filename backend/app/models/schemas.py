from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    """Task status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class LogLevel(str, Enum):
    """Log level enumeration"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Remove unused enums: ReaderType, SyncMode


class SyncTaskCreate(BaseModel):
    """Create sync task"""

    name: str = Field(..., description="Task name")
    custom_config: str = Field(
        ...,
        description="Custom TOML configuration content, must provide complete "
        "redis-shake configuration",
    )

    def validate_toml_config(self) -> List[str]:
        """Validate TOML configuration and return error messages list"""
        errors = []

        if not self.custom_config.strip():
            errors.append("TOML configuration content cannot be empty")
            return errors

        try:
            import toml

            config_data = toml.loads(self.custom_config)

            # Check required configuration sections
            required_sections = ["sync_reader", "redis_writer"]
            for section in required_sections:
                if section not in config_data:
                    errors.append(
                        f"Missing required configuration section: [{section}]"
                    )

            # Validate sync_reader configuration
            if "sync_reader" in config_data:
                sync_reader = config_data["sync_reader"]
                if "address" not in sync_reader:
                    errors.append("sync_reader section missing address configuration")

            # Validate redis_writer configuration
            if "redis_writer" in config_data:
                redis_writer = config_data["redis_writer"]
                if "address" not in redis_writer:
                    errors.append("redis_writer section missing address configuration")

        except Exception as e:
            errors.append(f"TOML configuration format error: {str(e)}")

        return errors


class SyncTask(BaseModel):
    """Sync task"""

    id: Optional[str] = Field(None, description="Task ID")
    name: str = Field(..., description="Task name")

    # Custom TOML configuration
    custom_config: str = Field(
        ...,
        description="Custom TOML configuration content, contains complete "
        "redis-shake configuration",
    )

    # Task status
    status: TaskStatus = Field(TaskStatus.PENDING, description="Task status")

    # Task execution information
    created_at: Optional[str] = Field(None, description="Creation time")
    started_at: Optional[str] = Field(None, description="Start time")
    completed_at: Optional[str] = Field(None, description="Completion time")
    error_message: Optional[str] = Field(None, description="Error message")

    # Process information
    process_id: Optional[int] = Field(None, description="Process ID")
    status_port: Optional[int] = Field(
        None, description="Redis-Shake status monitoring port"
    )

    # Progress information
    total_keys: Optional[int] = Field(0, description="Total key count")
    processed_keys: Optional[int] = Field(0, description="Processed key count")
    failed_keys: Optional[int] = Field(0, description="Failed key count")


class SyncTaskUpdate(BaseModel):
    """Update sync task"""

    name: Optional[str] = None
    status: Optional[TaskStatus] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    process_id: Optional[int] = None
    status_port: Optional[int] = None
    total_keys: Optional[int] = None
    processed_keys: Optional[int] = None
    failed_keys: Optional[int] = None
    custom_config: Optional[str] = Field(
        None, description="Custom TOML configuration content"
    )


class TaskLog(BaseModel):
    """Task log"""

    id: Optional[str] = Field(None, description="Log ID")
    task_id: str = Field(..., description="Task ID")
    task_name: Optional[str] = Field(None, description="Task name")
    timestamp: str = Field(..., description="Timestamp")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    source: Optional[str] = Field("system", description="Log source")

    model_config = ConfigDict(use_enum_values=True)


class TaskLogCreate(BaseModel):
    """Create task log"""

    task_id: str = Field(..., description="Task ID")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    source: Optional[str] = Field("system", description="Log source")


class APIResponse(BaseModel):
    """Unified API response format"""

    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None
