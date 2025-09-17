# Redis-Shake 管理平台后端

[English](README.md) | [中文](README_zh.md)

基于 FastAPI 开发的 Redis-Shake 管理平台后端服务，提供实时监控和任务管理功能。

## 功能特性

- **任务管理**: 创建、启动、停止和监控 Redis-Shake 任务
- **实时监控**: 集成 Redis-Shake 状态 API
- **配置管理**: TOML 配置文件处理
- **进程管理**: 自动进程生命周期管理
- **RESTful API**: 完整的 REST API 和 OpenAPI 文档

## 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Python 3.8+**: 支持 async/await 和类型提示
- **Pydantic**: 使用 Python 类型注解进行数据验证
- **aiohttp**: 异步 HTTP 客户端，用于 Redis-Shake 状态 API
- **Uvicorn**: ASGI 服务器实现

## 项目结构

```
app/
├── api/                    # API 路由
│   ├── __init__.py
│   └── sync_tasks.py      # 任务管理端点
├── core/                   # 核心配置
│   ├── __init__.py
│   └── config.py          # 应用设置
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── schemas.py         # Pydantic 模型
│   └── sync_task.py       # 任务数据模型
├── services/               # 业务逻辑
│   ├── __init__.py
│   └── task_service.py    # 任务管理服务
└── main.py                # 应用入口点
```

## 安装

```bash
pip install -r requirements.txt
```

## 开发

```bash
# 启动开发服务器（自动重载）
python -m app.main

# 或者直接使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后，访问以下地址查看 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 任务管理
- `GET /api/v1/tasks/` - 获取所有同步任务
- `POST /api/v1/tasks/` - 创建新的同步任务
- `GET /api/v1/tasks/{task_id}` - 获取特定任务详情
- `PUT /api/v1/tasks/{task_id}` - 更新任务配置
- `DELETE /api/v1/tasks/{task_id}` - 删除任务
- `POST /api/v1/tasks/{task_id}/start` - 启动任务执行
- `POST /api/v1/tasks/{task_id}/stop` - 停止任务执行

### 实时监控
- `GET /api/v1/tasks/{task_id}/realtime-status` - 获取实时任务状态
- `GET /api/v1/tasks/statistics/overview` - 获取系统概览统计

## 配置示例

### 基础同步任务
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

## 环境变量

使用环境变量配置应用：

- `REDIS_SHAKE_BIN_PATH` - redis-shake 二进制文件路径
- `REDIS_SHAKE_CONFIG_DIR` - 配置文件目录
- `REDIS_SHAKE_LOG_DIR` - 日志文件目录

## Docker 支持

```bash
# 构建镜像
docker build -t redis-shake-backend .

# 运行容器
docker run -p 8000:8000 redis-shake-backend
```

## 开发指南

### 代码规范
- 遵循 PEP 8 代码风格
- 使用类型提示
- 编写文档字符串
- 保持函数简洁

### 测试
```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app
```

## 贡献

欢迎提交 Issue 和 Pull Request！请查看 [贡献指南](../CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。
