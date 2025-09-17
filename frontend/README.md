# Redis-Shake Management Frontend

[English](README.md) | [中文](README_zh.md)

Modern React-based web interface for Redis-Shake management platform with real-time monitoring and intuitive task management.

## Features

### 🚀 **Task Management**
- ✅ Task list display (name, status, creation time, start time, process ID)
- ✅ Create new tasks (with TOML configuration support)
- ✅ Start/stop tasks with one click
- ✅ Edit task configurations
- ✅ Delete tasks with confirmation
- ✅ Real-time status updates (auto-refresh every 2 seconds)
- ✅ Empty state guidance
- ✅ Debug information panel

### 📊 **Real-time Monitoring**
- ✅ Live synchronization progress tracking
- ✅ Command-level statistics (SET, HSET, DEL, etc.)
- ✅ Data consistency checking
- ✅ Performance metrics and speed monitoring
- ✅ Interactive charts with ECharts
- ✅ Historical data visualization

### 📈 **Dashboard & Analytics**
- ✅ System overview with task statistics
- ✅ Resource monitoring
- ✅ Task status distribution
- ✅ Performance insights

### 🎨 **User Interface**
- ✅ Responsive design for all devices
- ✅ Modern Ant Design components
- ✅ Intuitive navigation menu
- ✅ Friendly error messages
- ✅ Loading state indicators
- ✅ Dark/light theme support

## Tech Stack

- **React 18.2** - Modern frontend framework with hooks
- **Ant Design 5.12** - Enterprise-class UI design language
- **React Router 6.8** - Declarative routing for React
- **Axios 1.6** - Promise-based HTTP client
- **ECharts** - Interactive data visualization charts
- **React Scripts 5.0** - Zero-configuration build tools

## Prerequisites

- **Node.js** 16+ and npm
- **Backend API** running on http://localhost:8000

## Quick Start

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

The application will start at http://localhost:3000 and automatically open in your browser.

### Production Build

```bash
npm run build
```

## Project Structure

```
src/
├── index.js              # Application entry point
├── App.js                # Main application component
├── index.css             # Global styles
├── services/
│   └── api.js            # API service layer
└── pages/
    ├── Dashboard.js      # Dashboard page
    ├── SyncTaskList.js   # Task management page
    └── TaskDetail.js     # Task detail monitoring page
```

## API Integration

The application connects to the backend API through proxy configuration:

- **Task API**: `/api/v1/tasks/`
- **Monitoring API**: `/api/v1/tasks/{id}/realtime-status`
- **Statistics API**: `/api/v1/tasks/statistics/overview`

### Key API Endpoints

- `GET /api/v1/tasks/` - Get task list
- `POST /api/v1/tasks/` - Create new task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/start` - Start task
- `POST /api/v1/tasks/{id}/stop` - Stop task
- `GET /api/v1/tasks/{id}/realtime-status` - Get real-time status

## Development

### Code Standards

- Use ESLint for code linting
- Follow React Hooks best practices
- Use functional components and hooks
- Consistent error handling and user feedback

### Debug Features

The task management page includes a debug information panel showing:
- API request status
- Task count
- Last update time
- Error messages (if any)

### State Management

- Uses React built-in useState and useEffect
- Component-level state management
- Automatic polling and real-time updates

## Deployment

### Development
```bash
npm start
```

### Production
```bash
npm run build
# Deploy the build directory to your web server
```

### Docker
```bash
# Build image
docker build -t redis-shake-frontend .

# Run container
docker run -p 3000:80 redis-shake-frontend
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend service is running on http://localhost:8000
   - Check proxy configuration in package.json

2. **Blank Page**
   - Check browser console for JavaScript errors
   - Ensure all dependencies are installed correctly

3. **Task Operations Failed**
   - Verify backend API is responding correctly
   - Check network requests in browser dev tools

### Debug Tips

- Open browser developer tools to view console logs
- Use Network tab to inspect API requests
- Enable debug information panel to view application state

## Contributing

We welcome Issues and Pull Requests to improve this project! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
