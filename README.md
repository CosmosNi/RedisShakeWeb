# Redis-Shake Management Platform

<div align="center">

![Redis-Shake Management Platform](https://img.shields.io/badge/Redis--Shake-Management%20Platform-red?style=for-the-badge&logo=redis)

[![CI/CD Pipeline](https://github.com/CosmosNi/RedisShakeWeb/actions/workflows/ci.yml/badge.svg)](https://github.com/CosmosNi/RedisShakeWeb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)](https://www.docker.com/)
[![Code Coverage](https://codecov.io/gh/CosmosNi/RedisShakeWeb/branch/main/graph/badge.svg)](https://codecov.io/gh/CosmosNi/RedisShakeWeb)
[![GitHub release](https://img.shields.io/github/release/CosmosNi/RedisShakeWeb.svg)](https://github.com/CosmosNi/RedisShakeWeb/releases)
[![GitHub stars](https://img.shields.io/github/stars/CosmosNi/RedisShakeWeb.svg?style=social&label=Star)](https://github.com/CosmosNi/RedisShakeWeb)

**A modern, web-based management platform for Redis-Shake with real-time monitoring and intuitive task management.**

[English](README.md) | [中文](README_zh.md)

[Features](#-features) • [Quick Start](#-quick-start) • [Demo](#-demo) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

## 📸 Demo

<div align="center">

### Dashboard Overview
![Dashboard](docs/images/dashboard-overview.png)

### Task Management
![Task Management](docs/images/task-management.png)

### Real-time Monitoring
![Monitoring](docs/images/real-time-monitoring.png)

</div>

## 🚀 Features

### 📊 **Real-time Monitoring**
- **Live synchronization progress** with interactive charts
- **Command-level statistics** (SET, HSET, DEL, etc.)
- **Data consistency checking** with real-time validation
- **Performance metrics** including sync speed and throughput
- **Visual progress indicators** with ECharts integration

### 🎛️ **Task Management**
- **Web-based interface** for creating and managing sync tasks
- **TOML configuration management** with automatic validation
- **Task lifecycle control** (create, start, stop, delete)
- **Multi-task support** with intelligent port allocation
- **Status tracking** with detailed error reporting

### 📈 **Dashboard & Analytics**
- **System overview** with task statistics
- **Historical data** tracking and analysis
- **Resource monitoring** and performance insights
- **Responsive design** for desktop and mobile devices

### 🔧 **Advanced Configuration**
- **Flexible filtering** by keys, databases, and commands
- **Custom Redis configurations** with template support
- **Automatic port management** to avoid conflicts
- **Error handling strategies** (panic/rewrite/skip)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   Redis-Shake   │
│                 │    │                  │    │                 │
│  • Task UI      │◄──►│  • REST API      │◄──►│  • Data Sync    │
│  • Monitoring   │    │  • Task Manager  │    │  • Status API   │
│  • Charts       │    │  • Config Mgmt   │    │  • Process Mgmt │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Frontend**: React 18.2, Ant Design 5.12, ECharts, Axios
- **Backend**: Python FastAPI, asyncio, aiohttp
- **Integration**: Redis-Shake native status API
- **Architecture**: RESTful API with real-time monitoring

## 📋 Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.8+
- **Redis** server (for testing)
- **Redis-Shake** binary ([Download here](https://github.com/tair-opensource/RedisShake/releases))

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended)

**For Linux/macOS:**
```bash
git clone https://github.com/CosmosNi/RedisShakeWeb.git
cd RedisShakeWeb
chmod +x cmd/start.sh
./cmd/start.sh
```

**For Windows:**
```cmd
git clone https://github.com/CosmosNi/RedisShakeWeb.git
cd RedisShakeWeb
cmd\start.bat
```

The startup script will automatically:
- ✅ Check prerequisites (Python, Node.js, npm)
- ✅ Install dependencies for both backend and frontend
- ✅ Start backend service on `http://localhost:8000`
- ✅ Start frontend service on `http://localhost:3000`
- ✅ Open the application in your browser

**To stop services:**
```bash
# Linux/macOS
./cmd/stop.sh

# Windows
cmd\stop.bat
```

**To check service status:**
```bash
# Linux/macOS
./cmd/stop.sh status

# Windows
cmd\stop.bat status
```

### Option 2: Manual Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/CosmosNi/RedisShakeWeb.git
cd RedisShakeWeb
```

#### 2. Setup Redis-Shake Binary

```bash
# Download Redis-Shake binary and place it in the bin/ directory
mkdir -p bin
# Download from: https://github.com/tair-opensource/RedisShake/releases
# Extract and place redis-shake binary in bin/redis-shake (Linux/macOS) or bin/redis-shake.exe (Windows)
```

#### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

The backend will start on `http://localhost:8000`

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will start on `http://localhost:3000`

#### 5. Access the Application

Open your browser and navigate to `http://localhost:3000` to access the Redis-Shake Management Platform.

## 📖 Documentation

### Project Structure

```
redis-shake-management/
├── cmd/                        # Startup Scripts
│   ├── start.sh               # Linux/macOS startup script
│   ├── stop.sh                # Linux/macOS stop script
│   ├── start.bat              # Windows startup script
│   └── stop.bat               # Windows stop script
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API Routes
│   │   ├── core/              # Core Configuration
│   │   ├── models/            # Data Models
│   │   ├── services/          # Business Logic
│   │   └── main.py           # Application Entry
│   ├── requirements.txt       # Python Dependencies
│   └── Dockerfile            # Docker Configuration
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/       # React Components
│   │   ├── pages/            # Page Components
│   │   ├── services/         # API Services
│   │   └── App.js           # Main App Component
│   ├── package.json          # Node.js Dependencies
│   └── public/               # Static Assets
├── bin/                       # Redis-Shake Binary
├── configs/                   # Configuration Files (auto-generated)
├── logs/                      # Log Files (auto-generated)
└── docs/                     # Documentation
```

### API Reference

#### Task Management
- `GET /api/v1/tasks/` - Get all sync tasks
- `POST /api/v1/tasks/` - Create a new sync task
- `GET /api/v1/tasks/{task_id}` - Get specific task details
- `PUT /api/v1/tasks/{task_id}` - Update task configuration
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `POST /api/v1/tasks/{task_id}/start` - Start task execution
- `POST /api/v1/tasks/{task_id}/stop` - Stop task execution

#### Real-time Monitoring
- `GET /api/v1/tasks/{task_id}/realtime-status` - Get real-time task status
- `GET /api/v1/tasks/statistics/overview` - Get system overview statistics

### Configuration Examples

#### Basic Sync Task
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

## 🐳 Docker Support

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Backend
cd backend
docker build -t redis-shake-backend .

# Frontend
cd frontend
docker build -t redis-shake-frontend .
```

## 🔧 Development

### Development Setup

1. **Backend Development**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m app.main --reload
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

- **Python**: Follow PEP 8, use `black` for formatting
- **JavaScript/React**: Use Prettier and ESLint
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Redis-Shake](https://github.com/tair-opensource/RedisShake) - The core data synchronization tool
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [React](https://reactjs.org/) - A JavaScript library for building user interfaces
- [Ant Design](https://ant.design/) - Enterprise-class UI design language

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/CosmosNi/RedisShakeWeb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CosmosNi/RedisShakeWeb/discussions)
- **Documentation**: [Wiki](https://github.com/CosmosNi/RedisShakeWeb/wiki)

## 🗺️ Roadmap

- [ ] **File Import/Export**: Support for RDB/AOF file operations
- [ ] **Advanced Filtering**: Visual filter configuration interface
- [ ] **Performance Analytics**: Detailed performance analysis tools
- [ ] **Multi-instance Support**: Support for multiple Redis-Shake instances
- [ ] **Backup Management**: Automated backup and restore features
- [ ] **Alert System**: Configurable alerts and notifications
- [ ] **Plugin System**: Extensible plugin architecture

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by the Redis-Shake Management Platform team

</div>