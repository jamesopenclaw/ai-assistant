import { useState, useRef, useEffect } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType,
  ModalForm,
  ProFormText,
  ProFormSelect
} from '@ant-design/pro-components';
import { 
  Button, 
  Space, 
  Tag, 
  Typography, 
  message, 
  Popconfirm,
  Switch
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined,
  DeleteOutlined,
  UserOutlined
} from '@ant-design/icons';
import styles from './index.less';

const { Text } = Typography;

// 获取租户 ID
const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

interface UserItem {
  user_id: string;
  username: string;
  email?: string;
  role: string;
  tenant_id: number;
  created_at: string;
  last_login?: string;
}

export default function UsersPage() {
  const actionRef = useRef<ActionType>();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载用户列表
  const loadUsers = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/users', {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = await res.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('加载用户失败:', err);
      message.error('加载用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // 创建用户
  const handleCreate = async (values: any) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify(values)
      });
      
      if (!res.ok) throw new Error('创建失败');
      
      message.success('创建成功');
      loadUsers();
      return true;
    } catch (err) {
      message.error('创建失败');
      return false;
    }
  };

  // 更新用户
  const handleUpdate = async (userId: string, values: any) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/users/${userId}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify(values)
      });
      
      if (!res.ok) throw new Error('更新失败');
      
      message.success('更新成功');
      loadUsers();
      return true;
    } catch (err) {
      message.error('更新失败');
      return false;
    }
  };

  // 删除用户
  const handleDelete = async (userId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (!res.ok) throw new Error('删除失败');
      
      message.success('删除成功');
      loadUsers();
    } catch (err) {
      message.error('删除失败');
    }
  };

  // 表格列定义
  const columns: ProColumns<UserItem>[] = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (_, record) => (
        <Space>
          <UserOutlined style={{ color: '#FF6B35' }} />
          <Text strong>{record.username}</Text>
        </Space>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      render: (val) => val || '-',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      render: (_, record) => {
        const color = record.role === 'admin' ? 'red' : record.role === 'guest' ? 'default' : 'blue';
        const text = record.role === 'admin' ? '管理员' : record.role === 'guest' ? '访客' : '用户';
        return <Tag color={color}>{text}</Tag>;
      },
      valueType: 'select',
      valueEnum: {
        admin: { text: '管理员', status: 'Error' },
        user: { text: '用户', status: 'Processing' },
        guest: { text: '访客', status: 'Default' },
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val) => val ? new Date(val).toLocaleString() : '-',
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      width: 180,
      render: (val) => val ? new Date(val).toLocaleString() : '未登录',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <ModalForm
            key="edit"
            title="编辑用户"
            trigger={
              <Button type="link" size="small" icon={<EditOutlined />}>
                编辑
              </Button>
            }
            onFinish={(values) => handleUpdate(record.user_id, values)}
          >
            <ProFormText
              name="username"
              label="用户名"
              placeholder="请输入用户名"
              initialValue={record.username}
              rules={[{ required: true }]}
            />
            <ProFormText
              name="email"
              label="邮箱"
              placeholder="请输入邮箱"
              initialValue={record.email}
            />
            <ProFormSelect
              name="role"
              label="角色"
              initialValue={record.role}
              options={[
                { label: '管理员', value: 'admin' },
                { label: '用户', value: 'user' },
                { label: '访客', value: 'guest' },
              ]}
              rules={[{ required: true }]}
            />
          </ModalForm>
          <Popconfirm
            title="确定删除此用户？"
            onConfirm={() => handleDelete(record.user_id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.usersContainer}>
      <ProTable<UserItem>
        actionRef={actionRef}
        columns={columns}
        dataSource={users}
        rowKey="user_id"
        loading={loading}
        search={false}
        pagination={{ pageSize: 10 }}
        toolBarRender={() => [
          <ModalForm
            key="create"
            title="创建用户"
            trigger={
              <Button type="primary" icon={<PlusOutlined />}>
                新建用户
              </Button>
            }
            onFinish={handleCreate}
          >
            <ProFormText
              name="username"
              label="用户名"
              placeholder="请输入用户名"
              rules={[{ required: true, message: '请输入用户名' }]}
            />
            <ProFormText
              name="email"
              label="邮箱"
              placeholder="请输入邮箱"
            />
            <ProFormText
              name="password"
              label="密码"
              placeholder="请输入密码"
              rules={[{ required: true, message: '请输入密码' }]}
            />
            <ProFormSelect
              name="role"
              label="角色"
              initialValue="user"
              options={[
                { label: '管理员', value: 'admin' },
                { label: '用户', value: 'user' },
                { label: '访客', value: 'guest' },
              ]}
              rules={[{ required: true }]}
            />
          </ModalForm>,
          <Button 
            key="refresh" 
            onClick={loadUsers}
            loading={loading}
          >
            刷新
          </Button>
        ]}
        headerTitle={
          <span>
            用户管理 | 当前租户: {getTenantId()} | 共 {users.length} 个用户
          </span>
        }
      />
    </div>
  );
}
