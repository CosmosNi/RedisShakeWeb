import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  DashboardOutlined,
  UnorderedListOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import SyncTaskList from './pages/SyncTaskList';
import TaskDetail from './pages/TaskDetail';
import TaskLogList from './pages/TaskLogList';

const { Header, Content, Sider } = Layout;

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '监控仪表板',
    },
    {
      key: '/sync-tasks',
      icon: <UnorderedListOutlined />,
      label: '同步任务',
    },
    {
      key: '/task-logs',
      icon: <FileTextOutlined />,
      label: '任务日志',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <div className="app-container" data-testid="app-container">
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ 
          background: '#1890ff', 
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <div style={{ 
            color: 'white', 
            fontSize: '20px', 
            fontWeight: 'bold' 
          }}>
            Redis-Shake Web管理平台
          </div>
        </Header>
        
        <Layout>
          <Sider width={200} style={{ background: '#fff' }}>
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              onClick={handleMenuClick}
              style={{ height: '100%', borderRight: 0 }}
            />
          </Sider>
          
          <Layout style={{ padding: '0' }}>
            <Content style={{ 
              background: '#fff', 
              margin: 0, 
              minHeight: 280 
            }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/sync-tasks" element={<SyncTaskList />} />
                <Route path="/task/:taskId" element={<TaskDetail />} />
                <Route path="/task-logs" element={<TaskLogList />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </div>
  );
}

export default App;
