import React, { useState, useEffect, useRef } from 'react';
import {
  Modal,
  Card,
  Typography,
  Space,
  Tag,
  Button,
  Alert,
  Spin,
  Switch,
  Tooltip,
  Empty
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ClearOutlined,
  DownloadOutlined,
  ReloadOutlined,
  DisconnectOutlined,
  LinkOutlined
} from '@ant-design/icons';

const { Text } = Typography;

const RealTimeLogModal = ({ visible, onClose, taskId, taskName }) => {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  const eventSourceRef = useRef(null);
  const logContainerRef = useRef(null);
  const pausedLogsRef = useRef([]);

  // 日志级别颜色映射
  const logLevelColors = {
    'DEBUG': 'default',
    'INFO': 'blue',
    'WARN': 'orange',
    'ERROR': 'red',
    'FATAL': 'red'
  };

  // 连接SSE
  const connectSSE = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsLoading(true);
    setError(null);
    setConnectionStatus('connecting');

    const eventSource = new EventSource(
      `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/logs/task/${taskId}/stream`
    );

    eventSource.onopen = () => {
      console.log('SSE connection opened');
      setIsLoading(false);
      setConnectionStatus('connected');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleSSEMessage(data);
      } catch (err) {
        console.error('Failed to parse SSE message:', err);
      }
    };

    eventSource.onerror = (event) => {
      console.error('SSE connection error:', event);
      setIsLoading(false);
      setConnectionStatus('error');
      setError('连接中断，正在尝试重连...');

      // 自动重连
      setTimeout(() => {
        if (visible && taskId) {
          connectSSE();
        }
      }, 3000);
    };

    eventSourceRef.current = eventSource;
  };

  // 处理SSE消息
  const handleSSEMessage = (data) => {
    switch (data.type) {
      case 'connected':
        setConnectionStatus('connected');
        setError(null);
        break;
        
      case 'log':
        const newLog = {
          id: `${data.timestamp}-${Math.random()}`,
          timestamp: data.timestamp,
          level: data.level,
          message: data.message,
          taskId: data.task_id
        };
        
        if (isPaused) {
          // 如果暂停，将日志存储到缓冲区
          pausedLogsRef.current.push(newLog);
        } else {
          // 直接添加到显示列表
          setLogs(prevLogs => [...prevLogs, newLog]);
        }
        break;
        
      case 'heartbeat':
        // 心跳消息，保持连接活跃
        break;
        
      case 'error':
        setError(data.message);
        setConnectionStatus('error');
        break;
        
      case 'disconnected':
        setConnectionStatus('disconnected');
        break;
        
      default:
        console.log('Unknown SSE message type:', data.type);
    }
  };

  // 断开SSE连接
  const disconnectSSE = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setConnectionStatus('disconnected');
  };

  // 清空日志
  const clearLogs = () => {
    setLogs([]);
    pausedLogsRef.current = [];
  };

  // 暂停/恢复日志显示
  const togglePause = () => {
    if (isPaused) {
      // 恢复：将缓冲区的日志添加到显示列表
      setLogs(prevLogs => [...prevLogs, ...pausedLogsRef.current]);
      pausedLogsRef.current = [];
    }
    setIsPaused(!isPaused);
  };

  // 导出日志
  const exportLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] [${log.level}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `task-${taskId}-logs-${new Date().toISOString().slice(0, 19)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // 自动滚动到底部
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  // 组件挂载时连接SSE
  useEffect(() => {
    if (visible && taskId) {
      connectSSE();
    }

    return () => {
      disconnectSSE();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible, taskId]);

  // 弹窗关闭时断开连接
  const handleClose = () => {
    disconnectSSE();
    setLogs([]);
    setError(null);
    pausedLogsRef.current = [];
    onClose();
  };

  // 连接状态指示器
  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <LinkOutlined style={{ color: '#52c41a' }} />;
      case 'connecting':
        return <Spin size="small" />;
      case 'error':
        return <DisconnectOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <DisconnectOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return '已连接';
      case 'connecting':
        return '连接中...';
      case 'error':
        return '连接错误';
      default:
        return '未连接';
    }
  };

  return (
    <Modal
      title={
        <Space>
          <span>实时日志 - {taskName || taskId}</span>
          <Tag color={connectionStatus === 'connected' ? 'green' : 'red'}>
            {getConnectionStatusIcon()}
            <span style={{ marginLeft: 4 }}>{getConnectionStatusText()}</span>
          </Tag>
        </Space>
      }
      open={visible}
      onCancel={handleClose}
      width={1000}
      height={600}
      footer={[
        <Space key="controls">
          <Tooltip title="暂停/恢复日志显示">
            <Button
              icon={isPaused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
              onClick={togglePause}
              type={isPaused ? "primary" : "default"}
            >
              {isPaused ? '恢复' : '暂停'}
            </Button>
          </Tooltip>
          
          <Tooltip title="清空当前显示的日志">
            <Button icon={<ClearOutlined />} onClick={clearLogs}>
              清空
            </Button>
          </Tooltip>
          
          <Tooltip title="导出日志到文件">
            <Button icon={<DownloadOutlined />} onClick={exportLogs} disabled={logs.length === 0}>
              导出
            </Button>
          </Tooltip>
          
          <Tooltip title="重新连接">
            <Button icon={<ReloadOutlined />} onClick={connectSSE} loading={isLoading}>
              重连
            </Button>
          </Tooltip>
          
          <Switch
            checkedChildren="自动滚动"
            unCheckedChildren="手动滚动"
            checked={autoScroll}
            onChange={setAutoScroll}
          />
        </Space>
      ]}
    >
      <div style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}
        
        {isPaused && pausedLogsRef.current.length > 0 && (
          <Alert
            message={`日志已暂停，缓冲区有 ${pausedLogsRef.current.length} 条新日志`}
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Card
          size="small"
          style={{ flex: 1, overflow: 'hidden' }}
          bodyStyle={{ padding: 0, height: '100%' }}
        >
          <div
            ref={logContainerRef}
            style={{
              height: '100%',
              overflow: 'auto',
              padding: '12px',
              backgroundColor: '#001529',
              color: '#fff',
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              fontSize: '12px',
              lineHeight: '1.5'
            }}
          >
            {logs.length === 0 ? (
              <Empty
                description="暂无日志数据"
                style={{ color: '#fff', marginTop: '100px' }}
              />
            ) : (
              logs.map((log) => (
                <div key={log.id} style={{ marginBottom: '4px' }}>
                  <Text style={{ color: '#666' }}>[{log.timestamp}]</Text>
                  <Tag
                    color={logLevelColors[log.level] || 'default'}
                    style={{ margin: '0 8px', minWidth: '50px', textAlign: 'center' }}
                  >
                    {log.level}
                  </Tag>
                  <Text style={{ color: '#fff' }}>{log.message}</Text>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </Modal>
  );
};

export default RealTimeLogModal;
