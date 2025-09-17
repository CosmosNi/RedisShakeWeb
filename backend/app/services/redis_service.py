import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional

import redis.asyncio as redis

from app.core.config import settings
from app.models.schemas import RedisConfig, RedisConfigCreate, RedisConfigUpdate


class RedisService:
    """Redis configuration management service"""

    def __init__(self):
        # Configuration file storage path
        self.config_file = os.path.join(
            settings.redis_shake_config_dir, "redis_configs.json"
        )
        self._ensure_config_file()

    def _ensure_config_file(self):
        """Ensure configuration file exists"""
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_configs(self) -> List[Dict]:
        """Load all configurations from file"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_configs(self, configs: List[Dict]):
        """Save configurations to file"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)

    async def get_all_configs(self) -> List[RedisConfig]:
        """Get allRedisconfiguration"""
        configs_data = self._load_configs()
        return [RedisConfig(**config) for config in configs_data]

    async def get_config(self, config_id: str) -> Optional[RedisConfig]:
        """Get Redis configuration by ID"""
        configs = await self.get_all_configs()
        for config in configs:
            if config.id == config_id:
                return config
        return None

    async def create_config(self, config_create: RedisConfigCreate) -> RedisConfig:
        """Create new Redis configuration"""
        # Generate unique ID
        config_id = str(uuid.uuid4())

        # Convert to dictionary and add ID
        config_dict = config_create.dict()
        config_dict["id"] = config_id

        # Createconfiguration
        config = RedisConfig(**config_dict)

        # Validate configuration
        validation_errors = config.validate_config()
        if validation_errors:
            raise ValueError(f"configurationfailed: {'; '.join(validation_errors)}")

        # Check if configuration name is duplicate
        existing_configs = self._load_configs()
        for existing_config in existing_configs:
            if existing_config.get("name") == config.name:
                raise ValueError(f"configuration '{config.name}' ")

        # Save configuration
        existing_configs.append(config_dict)
        self._save_configs(existing_configs)

        # Createconfiguration
        return config

    async def update_config(
        self, config_id: str, config_update: RedisConfigUpdate
    ) -> Optional[RedisConfig]:
        """UpdateRedisconfiguration"""
        configs = self._load_configs()

        # Updateconfiguration
        for i, config in enumerate(configs):
            if config["id"] == config_id:
                # Update fields
                update_data = config_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    if value is not None:
                        if key == "mode" and hasattr(value, "value"):
                            config[key] = value.value
                        else:
                            config[key] = value

                # Createconfiguration
                updated_config = RedisConfig(**config)

                # Validate configuration
                validation_errors = updated_config.validate_config()
                if validation_errors:
                    raise ValueError(f"configurationfailed: {'; '.join(validation_errors)}")

                # Check if configuration name is duplicate（configuration）
                if "name" in update_data:
                    for other_config in configs:
                        if (
                            other_config.get("id") != config_id
                            and other_config.get("name") == updated_config.name
                        ):
                            raise ValueError(f"configuration '{updated_config.name}' ")

                # Updateconfiguration
                self._save_configs(configs)

                # Updateconfiguration
                return updated_config

        return None

    async def delete_config(self, config_id: str) -> bool:
        """DeleteRedisconfiguration"""
        configs = self._load_configs()
        original_length = len(configs)

        # Deleteconfiguration
        configs = [config for config in configs if config["id"] != config_id]

        # configuration，Deletesuccessfully
        if len(configs) < original_length:
            self._save_configs(configs)
            return True

        return False

    async def test_connection(self, config_id: str) -> Dict[str, Any]:
        """TestRedisconnection"""
        config = await self.get_config(config_id)
        if not config:
            raise ValueError("configurationnot found")

        redis_client = None
        try:
            # RedisCreateconnection
            if config.mode == "standalone":
                # Standalone mode
                redis_client = redis.Redis(
                    host=config.host,
                    port=config.port,
                    password=config.password if config.password else None,
                    db=config.database,
                    socket_timeout=config.timeout,
                    decode_responses=True,
                )
            elif config.mode == "sentinel":
                # Sentinel mode
                if not config.sentinel_hosts or not config.master_name:
                    raise ValueError("Sentinel modeconfigurationsentinel_hostsmaster_name")

                sentinel_hosts = [
                    (host["host"], host["port"]) for host in config.sentinel_hosts
                ]
                sentinel = redis.Sentinel(
                    sentinel_hosts,
                    socket_timeout=config.timeout,
                    password=config.password if config.password else None,
                )
                redis_client = sentinel.master_for(
                    config.master_name,
                    password=config.password if config.password else None,
                    db=config.database,
                    decode_responses=True,
                )
            elif config.mode == "cluster":
                # Cluster mode
                if not config.cluster_nodes:
                    raise ValueError("Cluster modeconfigurationcluster_nodes")

                startup_nodes = [
                    {"host": node["host"], "port": node["port"]}
                    for node in config.cluster_nodes
                ]
                redis_client = redis.RedisCluster(
                    startup_nodes=startup_nodes,
                    password=config.password if config.password else None,
                    socket_timeout=config.timeout,
                    decode_responses=True,
                )
            else:
                raise ValueError(f"Unsupported Redis mode: {config.mode}")

            # Testconnection
            ping_result = await redis_client.ping()

            # Get Redis information
            info = await redis_client.info()
            redis_version = info.get("redis_version", "Unknown")

            return {
                "success": True,
                "message": "connectionsuccessfully",
                "data": {
                    "ping": ping_result,
                    "redis_version": redis_version,
                    "mode": config.mode,
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "Unknown"),
                },
            }
        except Exception as e:
            return {"success": False, "message": f"connectionfailed: {str(e)}"}
        finally:
            # connection
            if redis_client:
                try:
                    await redis_client.close()
                except:
                    pass
