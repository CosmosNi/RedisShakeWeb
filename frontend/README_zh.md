# Redis-Shake 管理平台前端

[English](README.md) | [中文](README_zh.md)

基于 React 18 和 Ant Design 5 开发的现代化 Redis-Shake 管理界面，提供实时监控和直观的任务管理功能。

## 功能特性

### 🚀 **任务管理**
- ✅ 任务列表展示（任务名称、状态、创建时间、开始时间、进程ID）
- ✅ 创建新任务（支持 TOML 配置）
- ✅ 一键启动/停止任务
- ✅ 编辑任务配置
- ✅ 删除任务（带确认）
- ✅ 实时状态更新（每2秒自动刷新）
- ✅ 空状态引导
- ✅ 调试信息面板

### 📊 **实时监控**
- ✅ 实时同步进度跟踪
- ✅ 命令级别统计（SET、HSET、DEL 等）
- ✅ 数据一致性检查
- ✅ 性能指标和速度监控
- ✅ ECharts 交互式图表
- ✅ 历史数据可视化

### 📈 **仪表板和分析**
- ✅ 系统概览和任务统计
- ✅ 资源监控
- ✅ 任务状态分布
- ✅ 性能洞察

### 🎨 **用户界面**
- ✅ 全设备响应式设计
- ✅ 现代化 Ant Design 组件
- ✅ 直观的导航菜单
- ✅ 友好的错误提示
- ✅ 加载状态指示器
- ✅ 深色/浅色主题支持

## 技术栈

- **React 18.2** - 现代化前端框架，支持 Hooks
- **Ant Design 5.12** - 企业级 UI 设计语言
- **React Router 6.8** - React 声明式路由
- **Axios 1.6** - 基于 Promise 的 HTTP 客户端
- **ECharts** - 交互式数据可视化图表
- **React Scripts 5.0** - 零配置构建工具

## 前置要求

- **Node.js** 16+ 和 npm
- **后端 API** 运行在 http://localhost:8000

## 快速开始

### 安装

```bash
npm install
```

### 开发

```bash
npm start
```

应用将在 http://localhost:3000 启动，并自动在浏览器中打开。

### 生产构建

```bash
npm run build
```

## 项目结构

```
src/
├── index.js              # 应用入口点
├── App.js                # 主应用组件
├── index.css             # 全局样式
├── services/
│   └── api.js            # API 服务层
└── pages/
    ├── Dashboard.js      # 仪表板页面
    ├── SyncTaskList.js   # 任务管理页面
    └── TaskDetail.js     # 任务详情监控页面
```

## API 集成

应用通过代理配置连接到后端 API：

- **任务 API**: `/api/v1/tasks/`
- **监控 API**: `/api/v1/tasks/{id}/realtime-status`
- **统计 API**: `/api/v1/tasks/statistics/overview`

### 主要 API 端点

- `GET /api/v1/tasks/` - 获取任务列表
- `POST /api/v1/tasks/` - 创建新任务
- `PUT /api/v1/tasks/{id}` - 更新任务
- `DELETE /api/v1/tasks/{id}` - 删除任务
- `POST /api/v1/tasks/{id}/start` - 启动任务
- `POST /api/v1/tasks/{id}/stop` - 停止任务
- `GET /api/v1/tasks/{id}/realtime-status` - 获取实时状态

## 开发

### 代码规范

- 使用 ESLint 进行代码检查
- 遵循 React Hooks 最佳实践
- 使用函数式组件和 Hooks
- 统一的错误处理和用户反馈

### 调试功能

任务管理页面包含调试信息面板，显示：
- API 请求状态
- 任务数量
- 最后更新时间
- 错误信息（如有）

### 状态管理

- 使用 React 内置的 useState 和 useEffect
- 组件级状态管理
- 自动轮询和实时更新

## 部署

### 开发环境
```bash
npm start
```

### 生产环境
```bash
npm run build
# 将 build 目录部署到 Web 服务器
```

### Docker
```bash
# 构建镜像
docker build -t redis-shake-frontend .

# 运行容器
docker run -p 3000:80 redis-shake-frontend
```

## 故障排除

### 常见问题

1. **API 连接失败**
   - 确保后端服务运行在 http://localhost:8000
   - 检查 package.json 中的代理配置

2. **页面空白**
   - 检查浏览器控制台是否有 JavaScript 错误
   - 确保所有依赖正确安装

3. **任务操作失败**
   - 验证后端 API 是否正常响应
   - 在浏览器开发工具中检查网络请求

### 调试技巧

- 打开浏览器开发者工具查看控制台日志
- 使用 Network 标签页检查 API 请求
- 启用调试信息面板查看应用状态

## 贡献

我们欢迎 Issue 和 Pull Request 来改进这个项目！请查看我们的 [贡献指南](../CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。
