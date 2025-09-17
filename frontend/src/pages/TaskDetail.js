import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Tag,
  Button,
  Space,
  Alert,
  Spin,
  Descriptions,
  Typography,
  message
} from 'antd';
import {
  ArrowLeftOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  DatabaseOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { taskApi } from '../services/api';
import RealTimeLogModal from '../components/RealTimeLogModal';

const { Title, Text } = Typography;

function TaskDetail() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [task, setTask] = useState(null);
  const [realTimeStatus, setRealTimeStatus] = useState(null);
  const [statusHistory, setStatusHistory] = useState([]);
  const [logModalVisible, setLogModalVisible] = useState(false);

  // 加载任务基本信息
  const loadTask = useCallback(async () => {
    try {
      const response = await taskApi.getTask(taskId);
      if (response.success) {
        setTask(response.data);
      }
    } catch (error) {
      console.error('Load task error:', error);
      message.error('加载任务信息失败');
    }
  }, [taskId]);

  // 加载实时状态
  const loadRealTimeStatus = useCallback(async () => {
    if (!task || task.status !== 'running') {
      return;
    }

    try {
      // 通过后端API获取实时状态
      const response = await taskApi.getRealtimeStatus(task.id);
      if (response.success) {
        const statusData = response.data;
        setRealTimeStatus(statusData);

        // 添加到历史记录
        const timestamp = new Date().toLocaleTimeString();
        setStatusHistory(prev => {
          const newHistory = [...prev, {
            time: timestamp,
            readOps: statusData.total_entries_count?.read_ops || 0,
            writeOps: statusData.total_entries_count?.write_ops || 0
          }];
          // 只保留最近20个数据点
          return newHistory.slice(-20);
        });
      }
    } catch (error) {
      console.error('Load real-time status error:', error);
    }
  }, [task]);

  // 获取任务状态配置
  const getStatusConfig = (status) => {
    const configs = {
      running: { color: 'green', icon: <PlayCircleOutlined />, text: '运行中' },
      stopped: { color: 'blue', icon: <PauseCircleOutlined />, text: '已停止' },
      failed: { color: 'red', icon: <ExclamationCircleOutlined />, text: '失败' }
    };
    return configs[status] || { color: 'default', icon: null, text: status };
  };

  // 计算同步进度
  const calculateProgress = () => {
    if (!realTimeStatus || !realTimeStatus.reader) {
      return 0;
    }

    const { rdb_file_size_bytes, rdb_received_bytes, status } = realTimeStatus.reader;

    // 如果RDB文件存在且已完全接收
    if (rdb_file_size_bytes > 0 && rdb_received_bytes >= rdb_file_size_bytes) {
      // RDB同步完成
      if (status === 'syncing aof') {
        // 正在同步AOF，认为是90%完成（因为AOF是增量的）
        return 90;
      } else {
        // 完全同步完成
        return 100;
      }
    }

    // 如果正在同步RDB
    if (rdb_file_size_bytes > 0 && rdb_received_bytes > 0) {
      return Math.round((rdb_received_bytes / rdb_file_size_bytes) * 80); // RDB占80%
    }

    // 默认情况
    return 0;
  };

  // 同步速度图表配置
  const getSpeedChartOption = () => {
    return {
      title: {
        text: '同步速度趋势',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          return `${params[0].name}<br/>
                  读取: ${params[0].value} ops/s<br/>
                  写入: ${params[1].value} ops/s`;
        }
      },
      legend: {
        data: ['读取速度', '写入速度']
      },
      xAxis: {
        type: 'category',
        data: statusHistory.map(item => item.time)
      },
      yAxis: {
        type: 'value',
        name: 'ops/s'
      },
      series: [
        {
          name: '读取速度',
          type: 'line',
          data: statusHistory.map(item => item.readOps),
          smooth: true,
          itemStyle: { color: '#1890ff' }
        },
        {
          name: '写入速度',
          type: 'line',
          data: statusHistory.map(item => item.writeOps),
          smooth: true,
          itemStyle: { color: '#52c41a' }
        }
      ]
    };
  };

  // 命令统计图表配置
  const getCommandChartOption = () => {
    if (!realTimeStatus || !realTimeStatus.per_cmd_entries_count) {
      return {};
    }

    const commands = Object.keys(realTimeStatus.per_cmd_entries_count);
    const data = commands.map(cmd => ({
      name: cmd,
      value: realTimeStatus.per_cmd_entries_count[cmd].read_count || 0
    }));

    return {
      title: {
        text: '命令类型分布',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      series: [
        {
          name: '命令统计',
          type: 'pie',
          radius: '50%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
  };

  useEffect(() => {
    if (taskId) {
      setLoading(true);
      loadTask().finally(() => setLoading(false));
    }
  }, [taskId, loadTask]);

  useEffect(() => {
    if (task) {
      // 立即加载一次状态
      loadRealTimeStatus();

      // 设置定时器，每2秒更新一次实时状态
      const interval = setInterval(loadRealTimeStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [task, loadRealTimeStatus]);

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!task) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="任务未找到"
          description="指定的任务不存在或已被删除"
          type="error"
          showIcon
        />
      </div>
    );
  }

  const statusConfig = getStatusConfig(task.status);
  const progress = calculateProgress();

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面头部 */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/sync-tasks')}
          >
            返回任务列表
          </Button>
          <Title level={3} style={{ margin: 0 }}>
            任务详情: {task.name}
          </Title>
        </Space>
        <Space>
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            onClick={() => setLogModalVisible(true)}
          >
            实时日志
          </Button>
          <Tag color={statusConfig.color} icon={statusConfig.icon} style={{ fontSize: '14px', padding: '4px 12px' }}>
            {statusConfig.text}
          </Tag>
        </Space>
      </div>

      <Spin spinning={loading}>
        {/* 基本信息 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Card title="基本信息">
              <Descriptions column={3}>
                <Descriptions.Item label="任务ID">{task.id}</Descriptions.Item>
                <Descriptions.Item label="任务名称">{task.name}</Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={statusConfig.color} icon={statusConfig.icon}>
                    {statusConfig.text}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {task.created_at ? new Date(task.created_at).toLocaleString() : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="启动时间">
                  {task.started_at ? new Date(task.started_at).toLocaleString() : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="进程ID">
                  {task.process_id || '-'}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
        </Row>

        {/* 实时监控数据 */}
        {task.status === 'running' && realTimeStatus && (
          <>
            {/* 实时统计 */}
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="同步进度"
                    value={progress}
                    suffix="%"
                    prefix={<SyncOutlined />}
                    valueStyle={{ color: progress === 100 ? '#52c41a' : '#1890ff' }}
                  />
                  <Progress percent={progress} size="small" style={{ marginTop: 8 }} />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="读取操作"
                    value={realTimeStatus.total_entries_count?.read_count || 0}
                    prefix={<DatabaseOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                  <Text type="secondary">
                    {realTimeStatus.total_entries_count?.read_ops || 0} ops/s
                  </Text>
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="写入操作"
                    value={realTimeStatus.total_entries_count?.write_count || 0}
                    prefix={<CheckCircleOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                  <Text type="secondary">
                    {realTimeStatus.total_entries_count?.write_ops || 0} ops/s
                  </Text>
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="数据一致性"
                    value={realTimeStatus.consistent ? '一致' : '不一致'}
                    prefix={realTimeStatus.consistent ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                    valueStyle={{ color: realTimeStatus.consistent ? '#52c41a' : '#ff4d4f' }}
                  />
                </Card>
              </Col>
            </Row>

            {/* 详细状态信息 */}
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col xs={24} lg={12}>
                <Card title="读取器状态">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="地址">
                      {realTimeStatus.reader?.address}
                    </Descriptions.Item>
                    <Descriptions.Item label="状态">
                      <Tag color="blue">{realTimeStatus.reader?.status}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="RDB文件大小">
                      {realTimeStatus.reader?.rdb_file_size_human}
                    </Descriptions.Item>
                    <Descriptions.Item label="RDB接收">
                      {realTimeStatus.reader?.rdb_received_human}
                    </Descriptions.Item>
                    <Descriptions.Item label="AOF偏移量">
                      {realTimeStatus.reader?.aof_received_offset}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title="写入器状态">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="名称">
                      {realTimeStatus.writer?.name}
                    </Descriptions.Item>
                    <Descriptions.Item label="未应答字节">
                      {realTimeStatus.writer?.unanswered_bytes || 0}
                    </Descriptions.Item>
                    <Descriptions.Item label="未应答条目">
                      {realTimeStatus.writer?.unanswered_entries || 0}
                    </Descriptions.Item>
                    <Descriptions.Item label="开始时间">
                      {realTimeStatus.start_time}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
            </Row>

            {/* 图表 */}
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card>
                  <ReactECharts 
                    option={getSpeedChartOption()} 
                    style={{ height: '300px' }}
                  />
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card>
                  <ReactECharts 
                    option={getCommandChartOption()} 
                    style={{ height: '300px' }}
                  />
                </Card>
              </Col>
            </Row>
          </>
        )}

        {/* 非运行状态提示 */}
        {task.status !== 'running' && (
          <Alert
            message="任务未运行"
            description="只有运行中的任务才能显示实时监控数据。请启动任务后查看详细监控信息。"
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Spin>

      {/* 实时日志弹窗 */}
      <RealTimeLogModal
        visible={logModalVisible}
        onClose={() => setLogModalVisible(false)}
        taskId={taskId}
        taskName={task?.name}
      />
    </div>
  );
}

export default TaskDetail;
