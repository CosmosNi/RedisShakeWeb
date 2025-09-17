import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  Table,
  Tag,
  Space,
  Button,
  Alert,
  Spin
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  TrophyOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';
import { taskApi } from '../services/api';

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState({
    total: 0,
    running: 0,
    stopped: 0,
    failed: 0,
    totalKeys: 0,
    processedKeys: 0,
    failedKeys: 0
  });
  const [recentTasks, setRecentTasks] = useState([]);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      // 获取统计数据
      const statsResponse = await taskApi.getStatistics();
      if (statsResponse.success) {
        const statsData = statsResponse.data;
        setStatistics({
          total: statsData.total,
          running: statsData.running,
          stopped: statsData.stopped,
          failed: statsData.failed,
          totalKeys: statsData.total_keys,
          processedKeys: statsData.processed_keys,
          failedKeys: statsData.failed_keys
        });
        setRecentTasks(statsData.recent_tasks || []);
      }


    } catch (error) {
      console.error('Load dashboard data error:', error);
    } finally {
      setLoading(false);
    }
  };



  // 任务状态分布图表配置
  const getTaskStatusChartOption = () => {
    return {
      title: {
        text: '任务状态分布',
        left: 'center',
        textStyle: {
          fontSize: 16
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: ['运行中', '已停止', '失败']
      },
      series: [
        {
          name: '任务状态',
          type: 'pie',
          radius: '50%',
          data: [
            { value: statistics.running, name: '运行中', itemStyle: { color: '#52c41a' } },
            { value: statistics.stopped, name: '已停止', itemStyle: { color: '#1890ff' } },
            { value: statistics.failed, name: '失败', itemStyle: { color: '#ff4d4f' } }
          ],
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

  // 数据处理进度图表配置
  const getDataProgressChartOption = () => {
    const processedRate = statistics.totalKeys > 0 
      ? ((statistics.processedKeys / statistics.totalKeys) * 100).toFixed(1)
      : 0;
    
    return {
      title: {
        text: '数据处理进度',
        left: 'center',
        textStyle: {
          fontSize: 16
        }
      },
      tooltip: {
        formatter: '{a} <br/>{b}: {c}%'
      },
      series: [
        {
          name: '处理进度',
          type: 'gauge',
          detail: {
            formatter: '{value}%'
          },
          data: [{ value: processedRate, name: '完成率' }]
        }
      ]
    };
  };

  // 最近任务表格列配置
  const recentTaskColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      ellipsis: true
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusConfig = {
          running: { color: 'green', icon: <PlayCircleOutlined />, text: '运行中' },
          stopped: { color: 'blue', icon: <PauseCircleOutlined />, text: '已停止' },
          failed: { color: 'red', icon: <ExclamationCircleOutlined />, text: '失败' }
        };
        const config = statusConfig[status] || { color: 'default', icon: null, text: status };
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time) => time ? new Date(time).toLocaleString() : '-'
    },
    {
      title: '处理键数',
      dataIndex: 'processed_keys',
      key: 'processed_keys',
      width: 100,
      render: (keys) => keys || 0
    }
  ];

  useEffect(() => {
    loadData();
    // 设置定时刷新
    const interval = setInterval(loadData, 10000); // 每10秒刷新
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>系统监控仪表板</h2>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={loadData}
          loading={loading}
        >
          刷新数据
        </Button>
      </div>

      <Spin spinning={loading}>
        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总任务数"
                value={statistics.total}
                prefix={<DatabaseOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="运行中"
                value={statistics.running}
                prefix={<PlayCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="已停止"
                value={statistics.stopped}
                prefix={<PauseCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="失败任务"
                value={statistics.failed}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 数据处理统计 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} md={8}>
            <Card title="数据处理统计">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Statistic
                  title="总键数"
                  value={statistics.totalKeys}
                  prefix={<TrophyOutlined />}
                />
                <Statistic
                  title="已处理"
                  value={statistics.processedKeys}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
                <Statistic
                  title="失败键数"
                  value={statistics.failedKeys}
                  prefix={<ExclamationCircleOutlined />}
                  valueStyle={{ color: '#ff4d4f' }}
                />
                <Progress
                  percent={statistics.totalKeys > 0 ? 
                    Math.round((statistics.processedKeys / statistics.totalKeys) * 100) : 0}
                  status={statistics.failedKeys > 0 ? 'exception' : 'active'}
                />
              </Space>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card>
              <ReactECharts 
                option={getTaskStatusChartOption()} 
                style={{ height: '300px' }}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card>
              <ReactECharts 
                option={getDataProgressChartOption()} 
                style={{ height: '300px' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 最近任务 */}
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card 
              title="最近任务" 
              extra={
                <Button type="link" onClick={() => navigate('/sync-tasks')}>
                  查看全部
                </Button>
              }
            >
              <Table
                columns={recentTaskColumns}
                dataSource={recentTasks}
                rowKey="id"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>

        {/* 系统状态提示 */}
        {statistics.failed > 0 && (
          <Alert
            message="系统告警"
            description={`检测到 ${statistics.failed} 个失败任务，请及时处理。`}
            type="warning"
            showIcon
            style={{ marginTop: 16 }}
            action={
              <Button size="small" type="primary" onClick={() => navigate('/sync-tasks')}>
                查看详情
              </Button>
            }
          />
        )}
      </Spin>
    </div>
  );
}

export default Dashboard;
