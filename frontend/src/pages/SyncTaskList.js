import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  message,
  Card,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { taskApi } from '../services/api';
import RealTimeLogModal from '../components/RealTimeLogModal';

const { TextArea } = Input;

function SyncTaskList() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [form] = Form.useForm();
  const [logModalVisible, setLogModalVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);


  // 默认TOML配置
  const defaultConfig = `[sync_reader]
cluster = false
address = "127.0.0.1:6379"
username = ""
password = ""
tls = false
sync_rdb = true
sync_aof = true
prefer_replica = false
try_diskless = false

[redis_writer]
cluster = false
address = "127.0.0.1:6380"
username = ""
password = ""
tls = false
off_reply = false

[filter]
allow_keys = []
allow_key_prefix = []
allow_key_suffix = []
allow_key_regex = []
block_keys = []
block_key_prefix = []
block_key_suffix = []
block_key_regex = []
allow_db = []
block_db = []
allow_command = []
block_command = []
allow_command_group = []
block_command_group = []
function = ""

[advanced]
dir = "data"
ncpu = 0
pprof_port = 0
status_port = 0
log_file = "shake.log"
log_level = "info"
log_interval = 5
log_rotation = true
log_max_size = 512
log_max_age = 7
log_max_backups = 3
log_compress = true
rdb_restore_command_behavior = "panic"
pipeline_count_limit = 1024
target_redis_client_max_querybuf_len = 1073741824
target_redis_proto_max_bulk_len = 512_000_000
aws_psync = ""
empty_db_before_sync = false

[module]
target_mbbloom_version = 20603`;

  // 加载任务列表
  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await taskApi.getTasks();
      console.log('Tasks loaded:', response);
      
      if (response.success) {
        setTasks(response.data || []);
      } else {
        throw new Error(response.message || '加载失败');
      }
    } catch (error) {
      console.error('Load tasks error:', error);
      message.error('加载任务列表失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadTasks();
    
    // 设置定时刷新
    const interval = setInterval(loadTasks, 10000);
    return () => clearInterval(interval);
  }, []);

  // 状态标签样式
  const getStatusTag = (status) => {
    const statusMap = {
      pending: { color: 'default', text: '待处理' },
      running: { color: 'processing', text: '运行中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
      stopped: { color: 'warning', text: '已停止' }
    };
    
    const config = statusMap[status] || { color: 'default', text: status };
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

  // 启动任务
  const handleStart = async (task) => {
    try {
      const response = await taskApi.startTask(task.id);
      if (response.success) {
        message.success('任务启动成功');
        loadTasks();
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      message.error('启动失败: ' + error.message);
    }
  };

  // 停止任务
  const handleStop = async (task) => {
    try {
      const response = await taskApi.stopTask(task.id);
      if (response.success) {
        message.success('任务停止成功');
        loadTasks();
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      message.error('停止失败: ' + error.message);
    }
  };

  // 删除任务
  const handleDelete = async (task) => {
    // 检查任务状态，如果是运行中的任务，给出友好提示
    if (task.status === 'running') {
      Modal.confirm({
        title: '无法删除运行中的任务',
        content: (
          <div>
            <p>任务 "{task.name}" 正在运行中，无法直接删除。</p>
            <p>请先停止任务，然后再进行删除操作。</p>
          </div>
        ),
        okText: '停止并删除',
        cancelText: '取消',
        onOk: async () => {
          try {
            // 先停止任务
            await taskApi.stopTask(task.id);
            message.success('任务已停止');

            // 等待一下确保状态更新
            setTimeout(async () => {
              try {
                // 再删除任务
                const response = await taskApi.deleteTask(task.id);
                if (response.success) {
                  message.success('删除成功');
                  loadTasks();
                } else {
                  message.error('删除失败，请手动重试');
                }
              } catch (deleteError) {
                console.error('Delete error:', deleteError);
                message.error('删除失败，请刷新页面后重试');
              }
            }, 1000);

          } catch (stopError) {
            console.error('Stop error:', stopError);
            message.error('停止任务失败，请手动停止后再删除');
          }
        }
      });
      return;
    }

    try {
      const response = await taskApi.deleteTask(task.id);
      if (response.success) {
        message.success('删除成功');
        loadTasks();
      } else {
        message.error(response.message || '删除失败');
      }
    } catch (error) {
      console.error('Delete error:', error);
      // 错误信息已经在api拦截器中处理了，这里不需要重复显示
      // 但为了保险起见，如果拦截器没有处理，这里提供兜底
      if (!error.response) {
        message.error('删除失败，请检查网络连接');
      }
    }
  };

  // 打开创建/编辑对话框
  const openModal = (task = null) => {
    setEditingTask(task);
    setModalVisible(true);
    
    if (task) {
      form.setFieldsValue({
        name: task.name,
        custom_config: task.custom_config || defaultConfig
      });
    } else {
      form.setFieldsValue({
        name: '',
        custom_config: defaultConfig
      });
    }
  };

  // 保存任务
  const handleSave = async (values) => {
    try {
      let response;
      if (editingTask) {
        response = await taskApi.updateTask(editingTask.id, values);
      } else {
        response = await taskApi.createTask(values);
      }
      
      if (response.success) {
        message.success(editingTask ? '更新成功' : '创建成功');
        setModalVisible(false);
        form.resetFields();
        setEditingTask(null);
        loadTasks();
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      message.error('保存失败: ' + error.message);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: formatDateTime,
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      key: 'started_at',
      width: 180,
      render: formatDateTime,
    },
    {
      title: '进程ID',
      dataIndex: 'process_id',
      key: 'process_id',
      width: 100,
      render: (pid) => pid || '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 300,
      render: (_, record) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/task/${record.id}`)}
          >
            详情
          </Button>
          <Button
            size="small"
            icon={<FileTextOutlined />}
            onClick={() => {
              setSelectedTask(record);
              setLogModalVisible(true);
            }}
          >
            日志
          </Button>
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleStart(record)}
            disabled={record.status === 'running'}
          >
            启动
          </Button>
          <Button
            size="small"
            icon={<PauseCircleOutlined />}
            onClick={() => handleStop(record)}
            disabled={record.status !== 'running'}
          >
            停止
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => openModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title={
              record.status === 'running'
                ? "任务正在运行中，确定要停止并删除吗？"
                : "确定要删除这个任务吗？"
            }
            description={
              record.status === 'running'
                ? "删除运行中的任务会先停止任务，然后删除相关配置。"
                : "删除后将无法恢复，请确认操作。"
            }
            onConfirm={() => handleDelete(record)}
            okText={record.status === 'running' ? "停止并删除" : "确定"}
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={record.status === 'running'}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">同步任务管理</h1>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openModal()}
          >
            创建任务
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadTasks}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>



      <Card>
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
          locale={{
            emptyText: (
              <div className="empty-container">
                <div>暂无任务数据</div>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => openModal()}
                  style={{ marginTop: 16 }}
                >
                  创建第一个任务
                </Button>
              </div>
            ),
          }}
        />
      </Card>

      {/* 创建/编辑任务对话框 */}
      <Modal
        title={editingTask ? '编辑任务' : '创建任务'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setEditingTask(null);
        }}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="请输入任务名称" />
          </Form.Item>
          
          <Form.Item
            name="custom_config"
            label="TOML配置"
            rules={[{ required: true, message: '请输入TOML配置' }]}
          >
            <TextArea
              rows={20}
              placeholder="请输入TOML配置"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingTask ? '更新' : '创建'}
              </Button>
              <Button onClick={() => {
                setModalVisible(false);
                form.resetFields();
                setEditingTask(null);
              }}>
                取消
              </Button>
              {!editingTask && (
                <Button
                  onClick={() => {
                    form.setFieldsValue({ custom_config: defaultConfig });
                  }}
                >
                  加载默认配置
                </Button>
              )}
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 实时日志弹窗 */}
      <RealTimeLogModal
        visible={logModalVisible}
        onClose={() => {
          setLogModalVisible(false);
          setSelectedTask(null);
        }}
        taskId={selectedTask?.id}
        taskName={selectedTask?.name}
      />
    </div>
  );
}

export default SyncTaskList;
