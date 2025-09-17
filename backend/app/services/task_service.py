import asyncio
import json
import os
import weakref
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiofiles
import aiohttp
import psutil

from app.core.config import settings
from app.models.schemas import (
    LogLevel,
    SyncTask,
    SyncTaskCreate,
    SyncTaskUpdate,
    TaskLogCreate,
    TaskStatus,
)
from app.services.log_service import LogService


class TaskService:
    """Sync task management service"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if TaskService._initialized:
            return
        TaskService._initialized = True

        # Task file storage path
        self.tasks_file = os.path.join(
            settings.redis_shake_config_dir, "sync_tasks.json"
        )
        self._ensure_tasks_file()
        # Service instances
        self.log_service = LogService()
        # Process output streams management
        self.process_streams = {}  # task_id -> {'process': process, 'log_buffer': []}
        self.stream_subscribers = {}  # task_id -> set of weak references to queues

    def _ensure_tasks_file(self):
        """Ensure task file exists"""
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    async def _read_process_output(
        self, task_id: str, process: asyncio.subprocess.Process
    ):
        """Read process output and distribute to subscribers"""
        try:
            # Start log file monitoring
            log_file_task = asyncio.create_task(self._monitor_log_file(task_id))

            # Read stdout
            async def read_stdout():
                while True:
                    try:
                        line = await process.stdout.readline()
                        if not line:
                            break
                        log_line = {
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": line.decode("utf-8").strip(),
                            "source": "stdout",
                        }
                        await self._distribute_log(task_id, log_line)
                    except Exception as e:
                        print(f"Error reading stdout for task {task_id}: {e}")
                        break

            # Read stderr
            async def read_stderr():
                while True:
                    try:
                        line = await process.stderr.readline()
                        if not line:
                            break
                        log_line = {
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": line.decode("utf-8").strip(),
                            "source": "stderr",
                        }
                        await self._distribute_log(task_id, log_line)
                    except Exception as e:
                        print(f"Error reading stderr for task {task_id}: {e}")
                        break

            # Start both readers concurrently
            await asyncio.gather(read_stdout(), read_stderr(), return_exceptions=True)

        except Exception as e:
            print(f"Error in process output reader for task {task_id}: {e}")
        finally:
            # Cancel log file monitoring
            if "log_file_task" in locals():
                log_file_task.cancel()

            # Clean up when process ends
            if task_id in self.process_streams:
                del self.process_streams[task_id]
            if task_id in self.stream_subscribers:
                del self.stream_subscribers[task_id]

    async def _monitor_log_file(self, task_id: str):
        """Monitor task-specific log file for changes"""
        log_file_path = self._get_task_log_file_path(task_id)
        last_position = 0

        try:
            while True:
                try:
                    if os.path.exists(log_file_path):
                        async with aiofiles.open(
                            log_file_path, "r", encoding="utf-8"
                        ) as f:
                            # Seek to last known position
                            await f.seek(last_position)

                            # Read new lines
                            while True:
                                line = await f.readline()
                                if not line:
                                    break

                                # Parse JSON log line
                                try:
                                    log_data = json.loads(line.strip())
                                    log_line = {
                                        "timestamp": log_data.get(
                                            "time", datetime.now().isoformat()
                                        ),
                                        "level": log_data.get("level", "INFO").upper(),
                                        "message": log_data.get("message", ""),
                                        "source": "redis-shake",
                                    }
                                    await self._distribute_log(task_id, log_line)
                                except json.JSONDecodeError:
                                    # If not JSON, treat as plain text
                                    log_line = {
                                        "timestamp": datetime.now().isoformat(),
                                        "level": "INFO",
                                        "message": line.strip(),
                                        "source": "redis-shake",
                                    }
                                    await self._distribute_log(task_id, log_line)

                            # Update last position
                            last_position = await f.tell()

                    # Wait before checking again
                    await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"Error monitoring log file for task {task_id}: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            print(f"Log file monitoring cancelled for task {task_id}")

    async def _distribute_log(self, task_id: str, log_line: dict):
        """Distribute log line to all subscribers"""
        # Store in buffer
        if task_id in self.process_streams:
            buffer = self.process_streams[task_id].get("log_buffer", [])
            buffer.append(log_line)
            # Keep only last 1000 lines
            if len(buffer) > 1000:
                buffer.pop(0)
            self.process_streams[task_id]["log_buffer"] = buffer

        # Send to subscribers
        if task_id in self.stream_subscribers:
            dead_refs = set()
            for queue_ref in self.stream_subscribers[task_id].copy():
                queue = queue_ref()
                if queue is None:
                    dead_refs.add(queue_ref)
                else:
                    try:
                        await queue.put(log_line)
                    except Exception:
                        dead_refs.add(queue_ref)

            # Clean up dead references
            self.stream_subscribers[task_id] -= dead_refs

    def subscribe_to_logs(self, task_id: str, queue: asyncio.Queue):
        """Subscribe to task logs"""
        if task_id not in self.stream_subscribers:
            self.stream_subscribers[task_id] = set()

        # Use weak reference to avoid memory leaks
        queue_ref = weakref.ref(queue)
        self.stream_subscribers[task_id].add(queue_ref)

        # Send existing buffer to new subscriber
        if task_id in self.process_streams:
            buffer = self.process_streams[task_id].get("log_buffer", [])
            asyncio.create_task(self._send_buffer_to_queue(queue, buffer))

    async def _send_buffer_to_queue(self, queue: asyncio.Queue, buffer: list):
        """Send buffered logs to a queue"""
        try:
            for log_line in buffer:
                await queue.put(log_line)
        except Exception as e:
            print(f"Error sending buffer to queue: {e}")

    def unsubscribe_from_logs(self, task_id: str, queue: asyncio.Queue):
        """Unsubscribe from task logs"""
        if task_id in self.stream_subscribers:
            # Find and remove the weak reference
            to_remove = None
            for queue_ref in self.stream_subscribers[task_id]:
                if queue_ref() is queue:
                    to_remove = queue_ref
                    break
            if to_remove:
                self.stream_subscribers[task_id].discard(to_remove)

    def _load_tasks(self) -> List[Dict]:
        """Load all tasks from file"""
        try:
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_tasks(self, tasks: List[Dict]):
        """Save tasks to file"""
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    async def get_all_tasks(self) -> List[SyncTask]:
        """Get all sync tasks"""
        tasks_data = self._load_tasks()
        return [SyncTask(**task) for task in tasks_data]

    async def get_task(self, task_id: str) -> Optional[SyncTask]:
        """Get sync task by ID"""
        tasks = await self.get_all_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    async def create_task(self, task_create: SyncTaskCreate) -> SyncTask:
        """Create new sync task"""
        # Validate TOML configuration
        validation_errors = task_create.validate_toml_config()
        if validation_errors:
            raise ValueError(f"TOMLconfigurationfailed: {'; '.join(validation_errors)}")

        # Check if task name is duplicate
        existing_tasks = self._load_tasks()
        for existing_task in existing_tasks:
            if existing_task.get("name") == task_create.name:
                raise ValueError(f"task '{task_create.name}' ")

        # Generate unique ID
        task_id = str(uuid.uuid4())

        # Create task object
        task_dict = {
            "id": task_id,
            "name": task_create.name,
            "custom_config": task_create.custom_config,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "process_id": None,
            "total_keys": 0,
            "processed_keys": 0,
            "failed_keys": 0,
        }

        # Save task
        existing_tasks.append(task_dict)
        self._save_tasks(existing_tasks)

        # Record log
        self.log_service.add_log(
            TaskLogCreate(
                task_id=task_id,
                level=LogLevel.INFO,
                message=f"task '{task_create.name}' Createsuccessfully",
            ),
            task_name=task_create.name,
        )

        # Return created task
        return SyncTask(**task_dict)

    async def update_task(
        self, task_id: str, task_update: SyncTaskUpdate
    ) -> Optional[SyncTask]:
        """Update sync task"""
        tasks = self._load_tasks()

        # Find and update task
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                # Check if task name is duplicate（task）
                if task_update.name and task_update.name != task.get("name"):
                    for other_task in tasks:
                        if (
                            other_task.get("id") != task_id
                            and other_task.get("name") == task_update.name
                        ):
                            raise ValueError(f"task '{task_update.name}' ")

                # Update fields
                update_data = task_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    if value is not None:
                        if key == "status" and hasattr(value, "value"):
                            task[key] = value.value
                        else:
                            task[key] = value

                # Save updated task
                self._save_tasks(tasks)

                # Return updated task
                return SyncTask(**task)

        return None

    async def delete_task(self, task_id: str) -> bool:
        """Delete sync task

        Note: Only non-running tasks can be deleted。
        If task is running, must stop task first before deletion。
        """
        # task
        task = await self.get_task(task_id)
        if not task:
            raise ValueError("tasknot found")

        # Check task status, running tasks cannot be deleted
        if task.status == TaskStatus.RUNNING:
            raise ValueError("Cannot delete running task, please stop task first")

        tasks = self._load_tasks()
        original_length = len(tasks)

        # Filter out task to be deleted
        tasks = [task for task in tasks if task["id"] != task_id]

        # If task count decreased, deletion was successful
        if len(tasks) < original_length:
            self._save_tasks(tasks)

            # Clean up related configuration files
            try:
                config_path = os.path.join(
                    settings.redis_shake_config_dir, f"task_{task_id}.toml"
                )
                if os.path.exists(config_path):
                    os.remove(config_path)
            except Exception as e:
                # configurationDeletefailedtaskDelete，Record log
                self.log_service.add_log(
                    TaskLogCreate(
                        task_id=task_id,
                        level=LogLevel.WARNING,
                        message=f"Delete configuration file failed: {str(e)}",
                    ),
                    task_name=task.name,
                )

            # Delete
            self.log_service.add_log(
                TaskLogCreate(
                    task_id=task_id,
                    level=LogLevel.INFO,
                    message=f"task '{task.name}' Deletesuccessfully",
                ),
                task_name=task.name,
            )

            return True

        return False

    def _ensure_status_port(self, config_content: str, task_id: str) -> str:
        """configuration"""
        import re

        # task（8080）
        status_port = 8080 + hash(task_id) % 1000

        # [advanced]
        if "[advanced]" in config_content:
            # status_port
            if re.search(r"status_port\s*=\s*\d+", config_content):
                # status_port，0，
                config_content = re.sub(
                    r"status_port\s*=\s*0",
                    f"status_port = {status_port}",
                    config_content,
                )
            else:
                # [advanced]status_port
                config_content = re.sub(
                    r"(\[advanced\])",
                    f"\\1\nstatus_port = {status_port}",
                    config_content,
                )
        else:
            # [advanced]status_port
            config_content += f"\n\n[advanced]\nstatus_port = {status_port}\n"

        return config_content

    def _ensure_task_specific_paths(self, config_content: str, task_id: str) -> str:
        """Ensure each task has its own working directory and log file"""
        import re

        # Create task-specific directory path
        task_data_dir = os.path.join(settings.redis_shake_data_dir, f"task_{task_id}")

        # Calculate relative path to redis-shake binary file
        redis_shake_dir = os.path.dirname(settings.redis_shake_bin_path)
        relative_data_dir = os.path.relpath(task_data_dir, redis_shake_dir)

        # Log file relative path to task data directory
        relative_log_file = "logs/" + f"task_{task_id}.log"

        # Update or add dir setting (use relative path)
        if re.search(r"dir\s*=", config_content):
            config_content = re.sub(
                r'dir\s*=\s*"[^"]*"', f'dir = "{relative_data_dir}"', config_content
            )
        else:
            # Add dir setting to [advanced] section
            if "[advanced]" in config_content:
                config_content = re.sub(
                    r"(\[advanced\])",
                    f'\\1\ndir = "{relative_data_dir}"',
                    config_content,
                )
            else:
                config_content += f'\n\n[advanced]\ndir = "{relative_data_dir}"\n'

        # Update or add log_file setting (use relative path to dir)
        if re.search(r"log_file\s*=", config_content):
            config_content = re.sub(
                r'log_file\s*=\s*"[^"]*"',
                f'log_file = "{relative_log_file}"',
                config_content,
            )
        else:
            # Add log_file setting to [advanced] section
            if "[advanced]" in config_content:
                config_content = re.sub(
                    r"(\[advanced\])",
                    f'\\1\nlog_file = "{relative_log_file}"',
                    config_content,
                )
            else:
                config_content += f'\n\n[advanced]\nlog_file = "{relative_log_file}"\n'

        return config_content

    def _get_task_log_file_path(self, task_id: str) -> str:
        """Get the log file path for a specific task"""
        task_data_dir = os.path.join(settings.redis_shake_data_dir, f"task_{task_id}")
        return os.path.join(task_data_dir, "logs", f"task_{task_id}.log")

    async def start_task(self, task_id: str) -> Dict[str, Any]:
        """Starttask"""
        # task
        task = await self.get_task(task_id)
        if not task:
            raise ValueError("tasknot found")

        # task
        if task.status not in [
            TaskStatus.PENDING,
            TaskStatus.STOPPED,
            TaskStatus.FAILED,
        ]:
            raise ValueError("、StopfailedtaskStart")

        # configuration
        if not task.custom_config:
            raise ValueError("TOMLconfiguration")

        try:
            # Create task-specific data directory
            task_data_dir = os.path.join(
                settings.redis_shake_data_dir, f"task_{task_id}"
            )
            os.makedirs(task_data_dir, exist_ok=True)

            # Create task log directory
            task_log_dir = os.path.join(task_data_dir, "logs")
            os.makedirs(task_log_dir, exist_ok=True)

            # Store configuration to task directory
            config_content = self._ensure_status_port(task.custom_config, task_id)
            config_content = self._ensure_task_specific_paths(config_content, task_id)
            config_path = os.path.join(task_data_dir, f"task_{task_id}.toml")

            # configuration
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)

            # Validate configurationCreatesuccessfully
            if not os.path.exists(config_path):
                raise ValueError(f"configurationCreatefailed: {config_path}")

            # redis-shake
            if not os.path.exists(settings.redis_shake_bin_path):
                raise ValueError(f"redis-shake: {settings.redis_shake_bin_path}")

            #
            cmd = [settings.redis_shake_bin_path, config_path]

            # Start
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(settings.redis_shake_bin_path),
            )

            # Store process and start reading output
            self.process_streams[task_id] = {"process": process, "log_buffer": []}

            # Start reading process output in background
            asyncio.create_task(self._read_process_output(task_id, process))

            # Start
            await asyncio.sleep(2)

            #
            if process.returncode is None:
                # ，Startsuccessfully
                #
                status_port = 8080 + hash(task_id) % 1000

                # Updatetask
                await self.update_task(
                    task_id,
                    SyncTaskUpdate(
                        status=TaskStatus.RUNNING,
                        started_at=datetime.now().isoformat(),
                        process_id=process.pid,
                        status_port=status_port,
                        error_message=None,
                    ),
                )

                # Record log
                self.log_service.add_log(
                    TaskLogCreate(
                        task_id=task_id,
                        level=LogLevel.INFO,
                        message=f"taskStartsuccessfully，ID: {process.pid}",
                    ),
                    task_name=task.name,
                )

                return {
                    "success": True,
                    "message": "taskStartsuccessfully",
                    "task_id": task_id,
                    "pid": process.pid,
                    "status_port": status_port,
                }
            else:
                # ，Startfailed
                stdout, stderr = await process.communicate()
                error_message = (
                    stderr.decode("utf-8")
                    if stderr
                    else stdout.decode("utf-8") if stdout else "taskStartfailed"
                )

                # Updatetaskfailed
                await self.update_task(
                    task_id,
                    SyncTaskUpdate(
                        status=TaskStatus.FAILED, error_message=error_message
                    ),
                )

                # Record log
                self.log_service.add_log(
                    TaskLogCreate(
                        task_id=task_id,
                        level=LogLevel.ERROR,
                        message=f"taskStartfailed: {error_message}",
                    ),
                    task_name=task.name,
                )

                return {
                    "success": False,
                    "message": "taskStartfailed",
                    "task_id": task_id,
                    "error": error_message,
                }

        except Exception as e:
            # Updatetaskfailed
            await self.update_task(
                task_id, SyncTaskUpdate(status=TaskStatus.FAILED, error_message=str(e))
            )
            raise ValueError(f"Starttaskfailed: {str(e)}")

    async def stop_task(self, task_id: str) -> Dict[str, Any]:
        """Stoptask"""
        # task
        task = await self.get_task(task_id)
        if not task:
            raise ValueError("tasknot found")

        # task
        if task.status != TaskStatus.RUNNING:
            raise ValueError("taskStop")

        try:
            success = False
            error_message = None

            # ID，
            if task.process_id:
                try:
                    #
                    if psutil.pid_exists(task.process_id):
                        process = psutil.Process(task.process_id)

                        #
                        process.terminate()

                        #
                        try:
                            process.wait(timeout=10)  # 10
                            success = True
                        except psutil.TimeoutExpired:
                            # 10，
                            process.kill()
                            process.wait(timeout=5)
                            success = True
                            error_message = ""
                    else:
                        #
                        success = True
                        error_message = ""

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    success = True
                    error_message = f": {str(e)}"
                except Exception as e:
                    error_message = f"Stopfailed: {str(e)}"
            else:
                success = True
                error_message = "ID"

            # UpdatetaskStop
            await self.update_task(
                task_id,
                SyncTaskUpdate(
                    status=TaskStatus.STOPPED,
                    completed_at=datetime.now().isoformat(),
                    process_id=None,
                ),
            )

            return {
                "success": success,
                "message": "taskStopsuccessfully" if success else "taskStopfailed",
                "task_id": task_id,
                "error": error_message,
            }

        except Exception as e:
            raise ValueError(f"Stoptaskfailed: {str(e)}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """task"""
        task = await self.get_task(task_id)
        if not task:
            raise ValueError("tasknot found")

        status_info = {
            "task_id": task_id,
            "status": task.status,
            "process_running": False,
            "process_info": None,
        }

        # task，
        if task.status == TaskStatus.RUNNING and task.process_id:
            try:
                if psutil.pid_exists(task.process_id):
                    process = psutil.Process(task.process_id)
                    status_info["process_running"] = True
                    status_info["process_info"] = {
                        "pid": task.process_id,
                        "cpu_percent": process.cpu_percent(),
                        "memory_info": process.memory_info()._asdict(),
                        "create_time": process.create_time(),
                    }
                else:
                    # ，Updatetask
                    await self.update_task(
                        task_id,
                        SyncTaskUpdate(
                            status=TaskStatus.FAILED,
                            error_message="",
                            completed_at=datetime.now().isoformat(),
                            process_id=None,
                        ),
                    )
                    status_info["status"] = TaskStatus.FAILED
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # ，Updatetask
                await self.update_task(
                    task_id,
                    SyncTaskUpdate(
                        status=TaskStatus.FAILED,
                        error_message="",
                        completed_at=datetime.now().isoformat(),
                        process_id=None,
                    ),
                )
                status_info["status"] = TaskStatus.FAILED

        return status_info

    async def get_tasks_statistics(self) -> Dict[str, Any]:
        """task"""
        tasks = await self.get_all_tasks()

        statistics = {
            "total": len(tasks),
            "running": 0,
            "stopped": 0,
            "failed": 0,
            "total_keys": 0,
            "processed_keys": 0,
            "failed_keys": 0,
            "recent_tasks": [],
        }

        for task in tasks:
            # task
            if task.status == TaskStatus.RUNNING:
                statistics["running"] += 1
            elif task.status == TaskStatus.STOPPED:
                statistics["stopped"] += 1
            elif task.status == TaskStatus.FAILED:
                statistics["failed"] += 1

            #
            statistics["total_keys"] += task.total_keys or 0
            statistics["processed_keys"] += task.processed_keys or 0
            statistics["failed_keys"] += task.failed_keys or 0

        # task（Create）
        sorted_tasks = sorted(tasks, key=lambda x: x.created_at, reverse=True)
        statistics["recent_tasks"] = [
            {
                "id": task.id,
                "name": task.name,
                "status": task.status.value,
                "created_at": task.created_at,
                "processed_keys": task.processed_keys or 0,
            }
            for task in sorted_tasks[:5]
        ]

        return statistics

    async def get_realtime_status(self, task_id: str) -> Dict[str, Any]:
        """taskRedis-Shake"""
        # task
        task = await self.get_task(task_id)
        if not task:
            raise ValueError("tasknot found")

        if task.status != TaskStatus.RUNNING:
            raise ValueError("task")

        if not task.status_port:
            raise ValueError("taskconfiguration")

        try:
            # HTTPRedis-Shake
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://localhost:{task.status_port}", timeout=5
                ) as response:
                    if response.status == 200:
                        status_data = await response.json()

                        # Updatetask
                        if "total_entries_count" in status_data:
                            total_count = status_data["total_entries_count"]
                            await self.update_task(
                                task_id,
                                SyncTaskUpdate(
                                    total_keys=total_count.get("read_count", 0),
                                    processed_keys=total_count.get("write_count", 0),
                                ),
                            )

                        return status_data
                    else:
                        raise ValueError(f"error: {response.status}")
        except asyncio.TimeoutError:
            raise ValueError("，task")
        except Exception as e:
            raise ValueError(f"failed: {str(e)}")

    async def recover_running_tasks(self) -> Dict[str, Any]:
        """task（）"""
        try:
            tasks = await self.get_all_tasks()
            recovered_tasks = []
            failed_tasks = []

            for task in tasks:
                if task.status == TaskStatus.RUNNING:
                    try:
                        #
                        if task.process_id and psutil.pid_exists(task.process_id):
                            # ，
                            continue

                        # ，Start
                        print(f"task: {task.name} (ID: {task.id})")

                        # Starttask
                        await self._restart_task(task)
                        recovered_tasks.append(
                            {
                                "task_id": task.id,
                                "task_name": task.name,
                                "status": "recovered",
                            }
                        )

                    except Exception as e:
                        print(
                            f"taskfailed: {task.name} (ID: {task.id}), error: {str(e)}"
                        )
                        # failedtaskUpdatefailed
                        await self.update_task(
                            task.id,
                            SyncTaskUpdate(
                                status=TaskStatus.FAILED,
                                error_message=f"failed: {str(e)}",
                            ),
                        )
                        failed_tasks.append(
                            {
                                "task_id": task.id,
                                "task_name": task.name,
                                "error": str(e),
                            }
                        )

            return {
                "recovered_count": len(recovered_tasks),
                "failed_count": len(failed_tasks),
                "recovered_tasks": recovered_tasks,
                "failed_tasks": failed_tasks,
            }

        except Exception as e:
            print(f"task: {str(e)}")
            return {
                "recovered_count": 0,
                "failed_count": 0,
                "recovered_tasks": [],
                "failed_tasks": [],
                "error": str(e),
            }

    async def _restart_task(self, task: SyncTask) -> None:
        """Starttask"""
        try:
            # Create task-specific data directory
            task_data_dir = os.path.join(
                settings.redis_shake_data_dir, f"task_{task.id}"
            )
            os.makedirs(task_data_dir, exist_ok=True)

            # Create task log directory
            task_log_dir = os.path.join(task_data_dir, "logs")
            os.makedirs(task_log_dir, exist_ok=True)

            # Store configuration to task directory
            config_path = os.path.join(task_data_dir, f"task_{task.id}.toml")

            # Ensure configuration file exists with proper paths
            config_content = self._ensure_status_port(task.custom_config, task.id)
            config_content = self._ensure_task_specific_paths(config_content, task.id)

            # Write updated configuration
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)

            # redis-shake
            if not os.path.exists(settings.redis_shake_bin_path):
                raise ValueError(f"redis-shake: {settings.redis_shake_bin_path}")

            #
            cmd = [settings.redis_shake_bin_path, config_path]

            # Start
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(settings.redis_shake_bin_path),
            )

            # Store process and start reading output
            self.process_streams[task.id] = {"process": process, "log_buffer": []}

            # Start reading process output in background
            asyncio.create_task(self._read_process_output(task.id, process))

            # Start
            await asyncio.sleep(2)

            #
            if process.returncode is None:
                # ，Startsuccessfully
                # configuration
                status_port = self._extract_status_port_from_config(config_path)
                if not status_port:
                    # configuration，
                    status_port = task.status_port or (8080 + hash(task.id) % 1000)

                # Updatetask
                await self.update_task(
                    task.id,
                    SyncTaskUpdate(
                        status=TaskStatus.RUNNING,
                        started_at=datetime.now().isoformat(),
                        process_id=process.pid,
                        status_port=status_port,
                        error_message=None,
                    ),
                )

                print(f"task {task.name} successfully，PID: {process.pid}")
            else:
                # Startfailed
                raise ValueError(f"redis-shakeStartfailed，: {process.returncode}")

        except Exception as e:
            raise ValueError(f"taskfailed: {str(e)}")

    def _extract_status_port_from_config(self, config_path: str) -> Optional[int]:
        """configuration"""
        try:
            import re

            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            # status_portconfiguration
            match = re.search(r"status_port\s*=\s*(\d+)", content)
            if match:
                port = int(match.group(1))
                # 0，configuration，None
                return port if port > 0 else None
            return None
        except Exception as e:
            print(f"configurationfailed: {str(e)}")
            return None
