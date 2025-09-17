import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Card,
  message,
  Popconfirm,
  DatePicker,
  Row,
  Col
} from 'antd';
import {
  ReloadOutlined,
  DeleteOutlined,
  SearchOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { logApi, taskApi } from '../services/api';

const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

function TaskLogList() {
  const [logs, setLogs] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    task_id: '',
    level: '',
    keyword: '',
    start_time: '',
    end_time: ''
  });

  // 日志级别配置
  const logLevels = [
    { value: 'DEBUG', color: 'default', text: 'DEBUG' },
    { value: 'INFO', color: 'blue', text: 'INFO' },
    { value: 'WARNING', color: 'orange', text: 'WARNING' },
    { value: 'ERROR', color: 'red', text: 'ERROR' },
    { value: 'CRITICAL', color: 'red', text: 'CRITICAL' }
  ];

  // 加载任务列表（用于过滤器）
  const loadTasks = async () => {
    try {
      const response = await taskApi.getTasks();
      if (response.success) {
        setTasks(response.data || []);
      }
    } catch (error) {
      console.error('Load tasks error:', error);
    }
  };

  // 加载日志列表
  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {};
      
      // 构建查询参数
      if (filters.task_id) params.task_id = filters.task_id;
      if (filters.level) params.level = filters.level;
      if (filters.keyword) params.keyword = filters.keyword;
      if (filters.start_time) params.start_time = filters.start_time;
      if (filters.end_time) params.end_time = filters.end_time;

      const response = await logApi.getLogs(params);
      console.log('Logs loaded:', response);
      
      if (response.success) {
        setLogs(response.data || []);
      } else {
        throw new Error(response.message || '加载失败');
      }
    } catch (error) {
      console.error('Load logs error:', error);
      message.error('加载日志失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadTasks();
    loadLogs();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 当过滤条件改变时重新加载
  useEffect(() => {
    loadLogs();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 获取日志级别标签
  const getLevelTag = (level) => {
    const config = logLevels.find(l => l.value === level) || 
                   { color: 'default', text: level };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 格式化时间
  const formatDateTime = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleString('zh-CN');
    } catch (e) {
      return dateStr;
    }
  };

  // 清除所有日志
  const handleClearAllLogs = async () => {
    try {
      const response = await logApi.clearLogs();
      if (response.success) {
        message.success('日志清除成功');
        loadLogs();
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      message.error('清除日志失败: ' + error.message);
    }
  };

  // 清除指定任务的日志 (暂未使用，但保留以备将来使用)
  // const handleClearTaskLogs = async (taskId) => {
  //   try {
  //     const response = await logApi.clearTaskLogs(taskId);
  //     if (response.success) {
  //       message.success('任务日志清除成功');
  //       loadLogs();
  //     } else {
  //       throw new Error(response.message);
  //     }
  //   } catch (error) {
  //     message.error('清除任务日志失败: ' + error.message);
  //   }
  // };

  // 重置过滤条件
  const resetFilters = () => {
    setFilters({
      task_id: '',
      level: '',
      keyword: '',
      start_time: '',
      end_time: ''
    });
  };

  // 处理时间范围选择
  const handleDateRangeChange = (dates, dateStrings) => {
    setFilters(prev => ({
      ...prev,
      start_time: dateStrings[0],
      end_time: dateStrings[1]
    }));
  };

  // 表格列定义
  const columns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: formatDateTime,
      sorter: (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
    },
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 120,
      ellipsis: true,
      render: (taskId) => {
        const task = tasks.find(t => t.id === taskId);
        return task ? task.name : (taskId || '-');
      },
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: getLevelTag,
      filters: logLevels.map(level => ({
        text: level.text,
        value: level.value,
      })),
      onFilter: (value, record) => record.level === value,
    },
    {
      title: '消息内容',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (text) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          {text}
        </span>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">任务日志</h1>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadLogs}
            loading={loading}
          >
            刷新
          </Button>
          <Popconfirm
            title="确定要清除所有日志吗？"
            onConfirm={handleClearAllLogs}
            okText="确定"
            cancelText="取消"
          >
            <Button
              danger
              icon={<DeleteOutlined />}
            >
              清除所有日志
            </Button>
          </Popconfirm>
        </Space>
      </div>

      {/* 过滤器 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="选择任务"
              value={filters.task_id}
              onChange={(value) => setFilters(prev => ({ ...prev, task_id: value }))}
              style={{ width: '100%' }}
              allowClear
            >
              {tasks.map(task => (
                <Option key={task.id} value={task.id}>
                  {task.name}
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="选择日志级别"
              value={filters.level}
              onChange={(value) => setFilters(prev => ({ ...prev, level: value }))}
              style={{ width: '100%' }}
              allowClear
            >
              {logLevels.map(level => (
                <Option key={level.value} value={level.value}>
                  {level.text}
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Search
              placeholder="搜索关键词"
              value={filters.keyword}
              onChange={(e) => setFilters(prev => ({ ...prev, keyword: e.target.value }))}
              onSearch={() => loadLogs()}
              enterButton={<SearchOutlined />}
            />
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Space>
              <Button
                icon={<ClearOutlined />}
                onClick={resetFilters}
              >
                重置
              </Button>
            </Space>
          </Col>
        </Row>
        
        <Row style={{ marginTop: 16 }}>
          <Col xs={24} md={12}>
            <RangePicker
              showTime
              placeholder={['开始时间', '结束时间']}
              onChange={handleDateRangeChange}
              style={{ width: '100%' }}
            />
          </Col>
        </Row>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={logs}
          rowKey={(record, index) => `${record.timestamp}-${index}`}
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条日志`,
          }}
          scroll={{ x: 800 }}
          locale={{
            emptyText: (
              <div className="empty-container">
                <div>暂无日志数据</div>
                <Button
                  type="primary"
                  icon={<ReloadOutlined />}
                  onClick={loadLogs}
                  style={{ marginTop: 16 }}
                >
                  刷新数据
                </Button>
              </div>
            ),
          }}
        />
      </Card>
    </div>
  );
}

export default TaskLogList;
