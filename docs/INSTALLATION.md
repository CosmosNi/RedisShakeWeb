# Installation Guide

This guide will help you set up the Redis-Shake Management Platform on your system.

## Prerequisites

Before installing, ensure you have the following software installed:

- **Node.js** 16.0 or higher
- **Python** 3.8 or higher
- **Redis** server (for testing)
- **Git** (for cloning the repository)

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/redis-shake-management.git
cd redis-shake-management
```

## Step 2: Download Redis-Shake Binary

1. Visit the [Redis-Shake releases page](https://github.com/tair-opensource/RedisShake/releases)
2. Download the appropriate binary for your operating system
3. Extract and place the `redis-shake` binary in the `bin/` directory

```bash
# Example for Linux/macOS
mkdir -p bin
# Download and extract redis-shake binary to bin/redis-shake
chmod +x bin/redis-shake
```

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend service
python -m app.main
```

The backend will be available at `http://localhost:8000`

## Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Step 5: Verify Installation

1. Open your browser and navigate to `http://localhost:3000`
2. You should see the Redis-Shake Management Platform interface
3. Check that the backend API is accessible at `http://localhost:8000/docs`

## Docker Installation (Alternative)

If you prefer using Docker:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

### Backend Configuration

The backend configuration is located in `backend/app/core/config.py`. You can override settings using environment variables:

```bash
export REDIS_SHAKE_BIN_PATH="/path/to/redis-shake"
export REDIS_SHAKE_CONFIG_DIR="/path/to/configs"
```

### Frontend Configuration

The frontend automatically connects to the backend at `http://localhost:8000`. If you need to change this, modify the proxy setting in `package.json`.

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Permission errors**: Make sure the redis-shake binary is executable
3. **Module not found**: Ensure all dependencies are installed correctly

### Getting Help

- Check the [FAQ](FAQ.md)
- Open an [issue](https://github.com/your-username/redis-shake-management/issues)
- Join our [discussions](https://github.com/your-username/redis-shake-management/discussions)
