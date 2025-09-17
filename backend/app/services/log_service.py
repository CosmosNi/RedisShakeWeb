import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.models.schemas import LogLevel, TaskLog, TaskLogCreate


class LogService:
    """Task log management service"""

    def __init__(self):
        # Log file storage path
        self.logs_file = os.path.join(settings.redis_shake_log_dir, "task_logs.json")
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.max_logs_per_task = 1000  # Keep maximum 1000 logs per task
        self._ensure_logs_file()

    def _ensure_logs_file(self):
        """Ensure log file exists"""
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_logs(self) -> List[dict]:
        """Load all logs from file"""
        try:
            with open(self.logs_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_logs(self, logs: List[dict]):
        """Save logs to file"""
        # ，
        if os.path.exists(self.logs_file):
            file_size = os.path.getsize(self.logs_file)
            if file_size > self.max_log_size:
                self._rotate_log_file()

        with open(self.logs_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def _rotate_log_file(self):
        """"""
        if os.path.exists(self.logs_file):
            backup_file = f"{self.logs_file}.backup"
            if os.path.exists(backup_file):
                os.remove(backup_file)
            os.rename(self.logs_file, backup_file)

    def add_log(
        self, task_log_create: TaskLogCreate, task_name: Optional[str] = None
    ) -> TaskLog:
        """Add task log"""
        log_id = str(uuid.uuid4())

        log = TaskLog(
            id=log_id,
            task_id=task_log_create.task_id,
            task_name=task_name,
            timestamp=datetime.now().isoformat(),
            level=task_log_create.level,
            message=task_log_create.message,
            source=task_log_create.source,
        )

        logs = self._load_logs()
        logs.append(log.dict())

        # Limit log count per task
        self._limit_logs_per_task(logs, task_log_create.task_id)

        self._save_logs(logs)

        return log

    def _limit_logs_per_task(self, logs: List[dict], task_id: str):
        """Limit log count per task"""
        task_logs = [log for log in logs if log["task_id"] == task_id]
        if len(task_logs) > self.max_logs_per_task:
            # ，
            task_logs.sort(key=lambda x: x["timestamp"], reverse=True)
            logs_to_keep = task_logs[: self.max_logs_per_task]

            # 
            other_logs = [log for log in logs if log["task_id"] != task_id]
            logs.clear()
            logs.extend(other_logs + logs_to_keep)

    def get_logs_by_task(
        self, task_id: str, limit: int = 100, level: Optional[str] = None
    ) -> List[TaskLog]:
        """Get logs by task ID"""
        logs = self._load_logs()
        task_logs = [log for log in logs if log["task_id"] == task_id]

        # Filter by log level
        if level:
            task_logs = [
                log
                for log in task_logs
                if log.get("level", "").upper() == level.upper()
            ]

        # Sort by time descending and limit count
        task_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        task_logs = task_logs[:limit]

        return [TaskLog(**log) for log in task_logs]

    def get_all_logs(
        self,
        limit: int = 100,
        level: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> List[TaskLog]:
        """Get all"""
        logs = self._load_logs()

        # Task ID filter
        if task_id:
            logs = [log for log in logs if log["task_id"] == task_id]

        # Filter by log level
        if level:
            logs = [
                log for log in logs if log.get("level", "").upper() == level.upper()
            ]

        # Sort by time descending and limit count
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        logs = logs[:limit]

        return [TaskLog(**log) for log in logs]

    def search_logs(self, keyword: str, limit: int = 100) -> List[TaskLog]:
        """"""
        logs = self._load_logs()

        # Search for keywords in messages
        matching_logs = []
        for log in logs:
            if keyword.lower() in log.get("message", "").lower():
                matching_logs.append(log)

        # Sort by time descending and limit count
        matching_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        matching_logs = matching_logs[:limit]

        return [TaskLog(**log) for log in matching_logs]

    def clear_logs_by_task(self, task_id: str) -> bool:
        """Clear logs for specified task"""
        logs = self._load_logs()
        original_length = len(logs)

        # Filter out logs for specified task
        logs = [log for log in logs if log["task_id"] != task_id]

        # ，Deletesuccessfully
        if len(logs) < original_length:
            self._save_logs(logs)
            return True

        return False

    def clear_all_logs(self) -> bool:
        """"""
        try:
            with open(self.logs_file, "w", encoding="utf-8") as f:
                json.dump([], f)
            return True
        except Exception:
            return False
