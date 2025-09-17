import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.data);
    return response.data;
  },
  (error) => {
    console.error('Response Error:', error);

    // 优先获取后端返回的错误信息
    // FastAPI使用detail字段，自定义API使用message字段
    let errorMessage = '请求失败';

    if (error.response?.data) {
      const data = error.response.data;
      errorMessage = data.detail || data.message || data.error || errorMessage;
    } else if (error.message) {
      errorMessage = error.message;
    }

    // 针对常见错误状态码提供更友好的提示
    if (error.response?.status === 400) {
      // 400错误通常是业务逻辑错误，显示具体错误信息
      message.error(errorMessage);
    } else if (error.response?.status === 404) {
      message.error('请求的资源不存在');
    } else if (error.response?.status === 500) {
      message.error('服务器内部错误，请稍后重试');
    } else if (error.code === 'NETWORK_ERROR') {
      message.error('网络连接失败，请检查网络连接');
    } else if (error.code === 'ECONNABORTED') {
      message.error('请求超时，请稍后重试');
    } else {
      message.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

// 任务相关API
export const taskApi = {
  // 获取任务列表
  getTasks: () => api.get('/tasks/'),
  
  // 创建任务
  createTask: (data) => api.post('/tasks/', data),
  
  // 更新任务
  updateTask: (id, data) => api.put(`/tasks/${id}`, data),
  
  // 删除任务
  deleteTask: (id) => api.delete(`/tasks/${id}`),
  
  // 启动任务
  startTask: (id) => api.post(`/tasks/${id}/start`),
  
  // 停止任务
  stopTask: (id) => api.post(`/tasks/${id}/stop`),
  
  // 获取任务详情
  getTask: (id) => api.get(`/tasks/${id}`),

  // 获取任务统计信息
  getStatistics: () => api.get('/tasks/statistics/overview'),

  // 获取任务实时状态
  getRealtimeStatus: (id) => api.get(`/tasks/${id}/realtime-status`),
};

// 日志相关API
export const logApi = {
  // 获取日志列表
  getLogs: (params) => api.get('/logs/', { params }),
  
  // 获取指定任务的日志
  getTaskLogs: (taskId, params) => api.get(`/logs/task/${taskId}`, { params }),
  
  // 清除日志
  clearLogs: () => api.delete('/logs/'),
  
  // 清除指定任务的日志
  clearTaskLogs: (taskId) => api.delete(`/logs/task/${taskId}`),
};

export default api;
