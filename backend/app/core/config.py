import os
from typing import Optional

from pydantic import ConfigDict

try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    """Application configuration"""

    # Basic application configuration
    app_name: str = "Redis-Shake Web Management Platform"
    debug: bool = False

    # Redis-Shake configuration
    redis_shake_bin_path: str = os.path.join(BASE_DIR, "..", "bin", "redis-shake")
    redis_shake_config_dir: str = os.path.join(BASE_DIR, "..", "configs")
    redis_shake_log_dir: str = os.path.join(BASE_DIR, "..", "logs")
    redis_shake_data_dir: str = os.path.join(BASE_DIR, "..", "data")  # Data directory

    # Redis connection configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    # Task configuration
    max_concurrent_tasks: int = 5
    task_timeout: int = 3600  # 1 hour

    model_config = ConfigDict(env_file=".env")


# Create configuration instance
settings = Settings()

# Ensure necessary directories exist
os.makedirs(settings.redis_shake_config_dir, exist_ok=True)
os.makedirs(settings.redis_shake_log_dir, exist_ok=True)
os.makedirs(settings.redis_shake_data_dir, exist_ok=True)
