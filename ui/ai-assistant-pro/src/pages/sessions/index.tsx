import { useState, useRef, useEffect } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType,
  ModalForm,
  ProFormText
} from '@ant-design/pro-components';
import { 
  Button, 
  Space, 
  Typography, 
  message, 
  Tag,
  Popconfirm
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined,
  DeleteOutlined,
  MessageOutlined
} from '@ant-design/icons';
import styles from './index.less';

const { Text } = Typography;

// 获取租户 ID
const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

interface SessionItem {
  session_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export default function SessionsPage() {
  const actionRef = useRef<ActionType>();
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载 Session 列表
  const loadSessions = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/sessions', {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = await res.json();
      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('加载会话失败:', err);
      message.error('加载会话列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  // 创建 Session
  const handleCreate = async (values: { name?: string }) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify(values)
      });
      
      if (!res.ok) throw new Error('创建失败');
      
      message.success('创建成功');
      loadSessions();
      return true;
    } catch (err) {
      message.error('创建失败');
      return false;
    }
  };

  // 重命名 Session
  const handleRename = async (sessionId: string, name: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({ name })
      });
      
      if (!res.ok) throw new Error('重命名失败');
      
      message.success('重命名成功');
      loadSessions();
    } catch (err) {
      message.error('重命名失败');
    }
  };

  // 删除 Session
  const handleDelete = async (sessionId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (!res.ok) throw new Error('删除失败');
      
      message.success('删除成功');
      loadSessions();
    } catch (err) {
      message.error('删除失败');
    }
  };

  // 表格列定义
  const columns: ProColumns<SessionItem>[] = [
    {
      title: '会话名称',
      dataIndex: 'name',
      key: 'name',
      render: (_, record) => (
        <Space>
          <MessageOutlined style={{ color: '#FF6B35' }} />
          <Text strong>{record.name}</Text>
        </Space>
      ),
    },
    {
      title: '消息数',
      dataIndex: 'message_count',
      key: 'message_count',
      width: 100,
      render: (count) => <Tag color="blue">{count} 条</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val) => val ? new Date(val).toLocaleString() : '-',
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (val) => val ? new Date(val).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              // 简单实现：使用 prompt
              const newName = window.prompt('请输入新名称', record.name);
              if (newName && newName !== record.name) {
                handleRename(record.session_id, newName);
              }
            }}
          >
            重命名
          </Button>
          <Popconfirm
            title="确定删除此会话？"
            onConfirm={() => handleDelete(record.session_id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.sessionsContainer}>
      <ProTable<SessionItem>
        actionRef={actionRef}
        columns={columns}
        dataSource={sessions}
        rowKey="session_id"
        loading={loading}
        search={false}
        pagination={{ pageSize: 10 }}
        toolBarRender={() => [
          <ModalForm
            key="create"
            title="创建新会话"
            trigger={
              <Button type="primary" icon={<PlusOutlined />}>
                新建会话
              </Button>
            }
            onFinish={handleCreate}
          >
            <ProFormText
              name="name"
              label="会话名称"
              placeholder="请输入会话名称"
              rules={[{ required: false }]}
            />
          </ModalForm>,
          <Button 
            key="refresh" 
            onClick={loadSessions}
            loading={loading}
          >
            刷新
          </Button>
        ]}
        headerTitle={
          <span>
            会话管理 | 当前租户: {getTenantId()} | 共 {sessions.length} 个会话
          </span>
        }
      />
    </div>
  );
}
