# Redis-Shake 管理平台

<div align="center">

![Redis-Shake Management Platform](https://img.shields.io/badge/Redis--Shake-Management%20Platform-red?style=for-the-badge&logo=redis)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)

**现代化的 Redis-Shake Web 管理平台，提供实时监控和直观的任务管理功能。**

[English](README.md) | [中文](README_zh.md)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [文档](#-文档) • [贡献](#-贡献)

</div>

## 🚀 功能特性

### 📊 **实时监控**
- **实时同步进度** - 交互式图表显示同步进度
- **命令级别统计** - 详细的 SET、HSET、DEL 等命令统计
- **数据一致性检查** - 实时验证数据一致性
- **性能指标** - 包括同步速度和吞吐量监控
- **可视化进度指示器** - ECharts 集成的专业图表

### 🎛️ **任务管理**
- **Web 界面** - 创建和管理同步任务的 Web 界面
- **TOML 配置管理** - 自动验证配置文件
- **任务生命周期控制** - 创建、启动、停止、删除任务
- **多任务支持** - 智能端口分配
- **状态跟踪** - 详细的错误报告

### 📈 **仪表板和分析**
- **系统概览** - 任务统计信息
- **历史数据** - 跟踪和分析
- **资源监控** - 性能洞察
- **响应式设计** - 支持桌面和移动设备

### 🔧 **高级配置**
- **灵活过滤** - 按键、数据库和命令过滤
- **自定义 Redis 配置** - 模板支持
- **自动端口管理** - 避免冲突
- **错误处理策略** - panic/rewrite/skip 选项

## 🏗️ 架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React 前端    │    │  FastAPI 后端    │    │   Redis-Shake   │
│                 │    │                  │    │                 │
│  • 任务界面     │◄──►│  • REST API      │◄──►│  • 数据同步     │
│  • 监控面板     │    │  • 任务管理器    │    │  • 状态 API     │
│  • 图表展示     │    │  • 配置管理      │    │  • 进程管理     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ 技术栈

- **前端**: React 18.2, Ant Design 5.12, ECharts, Axios
- **后端**: Python FastAPI, asyncio, aiohttp
- **集成**: Redis-Shake 原生状态 API
- **架构**: RESTful API 与实时监控

## 📋 前置要求

- **Node.js** 16+ 和 npm
- **Python** 3.8+
- **Redis** 服务器（用于测试）
- **Redis-Shake** 二进制文件 ([下载地址](https://github.com/tair-opensource/RedisShake/releases))

## 🚀 快速开始

### 方式一：一键启动（推荐）

**Linux/macOS 系统：**
```bash
git clone https://github.com/your-username/redis-shake-management.git
cd redis-shake-management
chmod +x cmd/start.sh
./cmd/start.sh
```

**Windows 系统：**
```cmd
git clone https://github.com/your-username/redis-shake-management.git
cd redis-shake-management
cmd\start.bat
```

启动脚本将自动完成：
- ✅ 检查前置条件（Python、Node.js、npm）
- ✅ 安装前后端依赖
- ✅ 启动后端服务 `http://localhost:8000`
- ✅ 启动前端服务 `http://localhost:3000`
- ✅ 在浏览器中打开应用

**停止服务：**
```bash
# Linux/macOS
./cmd/stop.sh

# Windows
cmd\stop.bat
```

**查看服务状态：**
```bash
# Linux/macOS
./cmd/stop.sh status

# Windows
cmd\stop.bat status
```

### 方式二：手动设置

#### 1. 克隆仓库

```bash
git clone https://github.com/your-username/redis-shake-management.git
cd redis-shake-management
```

#### 2. 设置 Redis-Shake 二进制文件

```bash
# 下载 Redis-Shake 二进制文件并放置在 bin/ 目录中
mkdir -p bin
# 从以下地址下载: https://github.com/tair-opensource/RedisShake/releases
# 解压并将二进制文件放置在 bin/redis-shake (Linux/macOS) 或 bin/redis-shake.exe (Windows)
```

#### 3. 后端设置

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

后端将在 `http://localhost:8000` 启动

**API 文档:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 4. 前端设置

```bash
cd frontend
npm install
npm start
```

前端将在 `http://localhost:3000` 启动

#### 5. 访问应用

打开浏览器并导航到 `http://localhost:3000` 访问 Redis-Shake 管理平台。

## 📖 文档

### 项目结构

```
redis-shake-management/
├── cmd/                        # 启动脚本
│   ├── start.sh               # Linux/macOS 启动脚本
│   ├── stop.sh                # Linux/macOS 停止脚本
│   ├── start.bat              # Windows 启动脚本
│   └── stop.bat               # Windows 停止脚本
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── main.py           # 应用入口
│   ├── requirements.txt       # Python 依赖
│   └── Dockerfile            # Docker 配置
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/            # 页面组件
│   │   ├── services/         # API 服务
│   │   └── App.js           # 主应用组件
│   ├── package.json          # Node.js 依赖
│   └── public/               # 静态资源
├── bin/                       # Redis-Shake 二进制文件
├── configs/                   # 配置文件（自动生成）
├── logs/                      # 日志文件（自动生成）
└── docs/                     # 文档
```

### API 参考

#### 任务管理
- `GET /api/v1/tasks/` - 获取所有同步任务
- `POST /api/v1/tasks/` - 创建新的同步任务
- `GET /api/v1/tasks/{task_id}` - 获取特定任务详情
- `PUT /api/v1/tasks/{task_id}` - 更新任务配置
- `DELETE /api/v1/tasks/{task_id}` - 删除任务
- `POST /api/v1/tasks/{task_id}/start` - 启动任务执行
- `POST /api/v1/tasks/{task_id}/stop` - 停止任务执行

#### 实时监控
- `GET /api/v1/tasks/{task_id}/realtime-status` - 获取实时任务状态
- `GET /api/v1/tasks/statistics/overview` - 获取系统概览统计

### 配置示例

#### 基础同步任务
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

## 🐳 Docker 支持

### 使用 Docker Compose

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动 Docker 构建

```bash
# 后端
cd backend
docker build -t redis-shake-backend .

# 前端
cd frontend
docker build -t redis-shake-frontend .
```

## 🧪 开发

### 开发环境设置

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/redis-shake-management.git
   cd redis-shake-management
   ```

2. **后端开发**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m app.main
   ```

3. **前端开发**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### 代码规范

- **Python**: 遵循 PEP 8，使用类型提示
- **JavaScript**: 使用 ESLint，遵循 React 最佳实践
- **提交信息**: 使用 [Conventional Commits](https://conventionalcommits.org/)

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 🗺️ 路线图

### v1.1 (计划中)
- [ ] 文件导入/导出功能
- [ ] 高级过滤器界面
- [ ] 批量任务操作
- [ ] 任务模板管理

### v1.2 (计划中)
- [ ] 用户认证和权限管理
- [ ] 多语言支持
- [ ] 主题定制
- [ ] 移动端优化

### v2.0 (长期)
- [ ] 集群管理支持
- [ ] 高级监控和告警
- [ ] 插件系统
- [ ] 云原生部署

## 🤝 贡献

我们欢迎所有形式的贡献！请查看我们的 [贡献指南](CONTRIBUTING.md) 了解如何开始。

### 贡献者

感谢所有为这个项目做出贡献的人！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Redis-Shake](https://github.com/tair-opensource/RedisShake) - 强大的 Redis 数据同步工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [React](https://reactjs.org/) - 用于构建用户界面的 JavaScript 库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言

## 📞 支持

如果您有任何问题或需要帮助：

- 📖 查看 [文档](docs/)
- 🐛 提交 [Issue](https://github.com/your-username/redis-shake-management/issues)
- 💬 参与 [讨论](https://github.com/your-username/redis-shake-management/discussions)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

Made with ❤️ by the Redis-Shake Management Team

</div>
