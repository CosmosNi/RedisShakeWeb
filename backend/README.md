# Redis-Shake Management Backend

[English](README.md) | [中文](README_zh.md)

FastAPI-based backend service for Redis-Shake management platform with real-time monitoring and task management capabilities.

## Features

- **Task Management**: Create, start, stop, and monitor Redis-Shake tasks
- **Real-time Monitoring**: Integration with Redis-Shake status API
- **Configuration Management**: TOML configuration handling
- **Process Management**: Automatic process lifecycle management
- **RESTful API**: Comprehensive REST API with OpenAPI documentation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.8+**: Async/await support with type hints
- **Pydantic**: Data validation using Python type annotations
- **aiohttp**: Async HTTP client for Redis-Shake status API
- **Uvicorn**: ASGI server implementation

## Project Structure

```
app/
├── api/                    # API routes
│   ├── __init__.py
│   └── sync_tasks.py      # Task management endpoints
├── core/                   # Core configuration
│   ├── __init__.py
│   └── config.py          # Application settings
├── models/                 # Data models
│   ├── __init__.py
│   ├── schemas.py         # Pydantic models
│   └── sync_task.py       # Task data models
├── services/               # Business logic
│   ├── __init__.py
│   └── task_service.py    # Task management service
└── main.py                # Application entry point
```

## Installation

```bash
pip install -r requirements.txt
```

## Development

```bash
# Start development server with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

After starting the service, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Task Management
- `GET /api/v1/tasks/` - Get all sync tasks
- `POST /api/v1/tasks/` - Create a new sync task
- `GET /api/v1/tasks/{task_id}` - Get specific task details
- `PUT /api/v1/tasks/{task_id}` - Update task configuration
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `POST /api/v1/tasks/{task_id}/start` - Start task execution
- `POST /api/v1/tasks/{task_id}/stop` - Stop task execution

### Real-time Monitoring
- `GET /api/v1/tasks/{task_id}/realtime-status` - Get real-time task status
- `GET /api/v1/tasks/statistics/overview` - Get system overview statistics

## Configuration Examples

### Basic Sync Task
```toml
[sync_reader]
cluster = false
address = "127.0.0.1:6379"
username = ""
password = ""
tls = false
sync_rdb = true
sync_aof = true

[redis_writer]
cluster = false
address = "127.0.0.1:6380"
username = ""
password = ""
tls = false

[advanced]
status_port = 8080
log_level = "info"
```

## Environment Variables

Configure the application using environment variables:

- `REDIS_SHAKE_BIN_PATH` - Path to redis-shake binary
- `REDIS_SHAKE_CONFIG_DIR` - Configuration files directory
- `REDIS_SHAKE_LOG_DIR` - Log files directory

## Docker Support

```bash
# Build image
docker build -t redis-shake-backend .

# Run container
docker run -p 8000:8000 redis-shake-backend
```