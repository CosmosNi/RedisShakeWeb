import React from 'react';
import { Card, Row, Col, Button, Typography } from 'antd';
import {
  UnorderedListOutlined,
  FileTextOutlined,
  DashboardOutlined,
  RocketOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

function Home() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <DashboardOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      title: '监控仪表板',
      description: '实时监控系统状态，查看任务统计和性能指标',
      action: () => navigate('/dashboard'),
      buttonText: '查看仪表板'
    },
    {
      icon: <UnorderedListOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      title: '同步任务管理',
      description: '创建、启动、停止Redis数据同步任务，支持TOML配置文件管理',
      action: () => navigate('/sync-tasks'),
      buttonText: '管理任务'
    },
    {
      icon: <FileTextOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      title: '任务日志查看',
      description: '实时查看任务执行日志和状态，支持日志搜索和过滤',
      action: () => navigate('/task-logs'),
      buttonText: '查看日志'
    }
  ];

  return (
    <div className="page-container">
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <RocketOutlined style={{ fontSize: '64px', color: '#1890ff', marginBottom: '16px' }} />
        <Title level={1}>Redis-Shake Web管理平台</Title>
        <Paragraph style={{ fontSize: '16px', color: '#666' }}>
          基于React和Ant Design开发的Redis数据同步管理工具
        </Paragraph>
      </div>

      <Row gutter={[24, 24]} justify="center">
        {features.map((feature, index) => (
          <Col xs={24} sm={12} md={8} key={index}>
            <Card
              hoverable
              style={{ 
                textAlign: 'center', 
                height: '280px',
                display: 'flex',
                flexDirection: 'column'
              }}
              bodyStyle={{ 
                flex: 1, 
                display: 'flex', 
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ marginBottom: '16px' }}>
                  {feature.icon}
                </div>
                <Title level={3}>{feature.title}</Title>
                <Paragraph style={{ color: '#666' }}>
                  {feature.description}
                </Paragraph>
              </div>
              <Button 
                type="primary" 
                size="large"
                onClick={feature.action}
                style={{ marginTop: '16px' }}
              >
                {feature.buttonText}
              </Button>
            </Card>
          </Col>
        ))}
      </Row>

      <Card style={{ marginTop: '48px' }}>
        <Title level={3}>
          <SettingOutlined style={{ marginRight: '8px' }} />
          使用说明
        </Title>
        
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12}>
            <Title level={4}>📝 创建同步任务</Title>
            <ol style={{ paddingLeft: '20px' }}>
              <li>点击"同步任务"菜单进入任务管理页面</li>
              <li>点击"创建任务"按钮</li>
              <li>输入任务名称</li>
              <li>在TOML配置中填写源Redis和目标Redis的连接信息</li>
              <li>保存任务</li>
            </ol>
          </Col>
          
          <Col xs={24} md={12}>
            <Title level={4}>🚀 启动任务</Title>
            <ol style={{ paddingLeft: '20px' }}>
              <li>在任务列表中找到创建的任务</li>
              <li>点击"启动"按钮开始数据同步</li>
              <li>可以实时查看任务状态和进程状态</li>
              <li>需要停止时点击"停止"按钮</li>
            </ol>
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default Home;
