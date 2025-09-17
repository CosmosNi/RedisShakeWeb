import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.redis_config import router as redis_config_router
from app.api.sync_tasks import router as sync_tasks_router
from app.api.task_logs import router as task_logs_router
from app.core.config import settings
from app.services.task_service import TaskService

# Global task service instance
task_service = TaskService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Execute on startup
    print("🚀 Redis-Shake Web Management Platform starting...")

    # Recover running tasks
    try:
        print("🔄 Checking and recovering running tasks...")
        recovery_result = await task_service.recover_running_tasks()

        if recovery_result["recovered_count"] > 0:
            print(f"✅ Successfully recovered {recovery_result['recovered_count']} tasks")
            for task in recovery_result["recovered_tasks"]:
                print(f"   - {task['task_name']} (ID: {task['task_id']})")

        if recovery_result["failed_count"] > 0:
            print(f"❌ {recovery_result['failed_count']} tasks failed to recover")
            for task in recovery_result["failed_tasks"]:
                print(
                    f"   - {task['task_name']} (ID: {task['task_id']}): {task['error']}"
                )

        if (
            recovery_result["recovered_count"] == 0
            and recovery_result["failed_count"] == 0
        ):
            print("ℹ️  No tasks need to be recovered")

    except Exception as e:
        print(f"❌ Task recovery process error: {str(e)}")

    print("✅ Redis-Shake Web Management Platform started successfully!")

    yield

    # Execute on shutdown
    print("🛑 Redis-Shake Web Management Platform is shutting down...")


app = FastAPI(
    title="Redis-Shake Web Management Platform",
    description="Redis-Shake Web Management Interface based on FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, should set specific frontend addresses
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(redis_config_router, prefix="/api/v1/redis", tags=["Redis Config"])
app.include_router(sync_tasks_router, prefix="/api/v1/tasks", tags=["Sync Tasks"])
app.include_router(task_logs_router, prefix="/api/v1/logs", tags=["Task Logs"])


@app.get("/")
async def root():
    return {"message": "Redis-Shake Web Management Platform API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
