import { useState, useRef, useEffect } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType,
  ModalForm,
  ProFormText,
  ProFormSelect,
  ProFormSwitch
} from '@ant-design/pro-components';
import { 
  Button, 
  Space, 
  Tag, 
  Typography, 
  message, 
  Popconfirm,
  Card
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined,
  DeleteOutlined,
  ApiOutlined,
  CheckCircleFilled
} from '@ant-design/icons';
import styles from './index.less';

const { Text } = Typography;

// 获取租户 ID
const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

interface ModelItem {
  model_id: string;
  name: string;
  provider: string;
  api_key: string;
  base_url?: string;
  model_name: string;
  enabled: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

const providerMap: Record<string, { text: string; color: string }> = {
  minimax: { text: 'MiniMax', color: 'blue' },
  openai: { text: 'OpenAI', color: 'green' },
  douyin: { text: '豆包', color: 'orange' },
  deepseek: { text: 'DeepSeek', color: 'cyan' },
  qwen: { text: '阿里千问', color: 'purple' },
};

export default function ModelsPage() {
  const actionRef = useRef<ActionType>();
  const [models, setModels] = useState<ModelItem[]>([]);
  const [providers, setProviders] = useState<any>({});
  const [loading, setLoading] = useState(false);

  // 加载模型配置
  const loadModels = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const [modelsRes, providersRes] = await Promise.all([
        fetch('/api/models', { headers: { 'X-Tenant-ID': tenantId } }),
        fetch('/api/models/providers')
      ]);
      
      const modelsData = await modelsRes.json();
      const providersData = await providersRes.json();
      
      setModels(Array.isArray(modelsData) ? modelsData : []);
      setProviders(providersData || {});
    } catch (err) {
      console.error('加载失败:', err);
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  // 创建模型
  const handleCreate = async (values: any) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/models', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify(values)
      });
      
      if (!res.ok) throw new Error('创建失败');
      
      message.success('创建成功');
      loadModels();
      return true;
    } catch (err) {
      message.error('创建失败');
      return false;
    }
  };

  // 更新模型
  const handleUpdate = async (modelId: string, values: any) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/models/${modelId}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify(values)
      });
      
      if (!res.ok) throw new Error('更新失败');
      
      message.success('更新成功');
      loadModels();
      return true;
    } catch (err) {
      message.error('更新失败');
      return false;
    }
  };

  // 删除模型
  const handleDelete = async (modelId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/models/${modelId}`, {
        method: 'DELETE',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (!res.ok) throw new Error('删除失败');
      
      message.success('删除成功');
      loadModels();
    } catch (err) {
      message.error('删除失败');
    }
  };

  // 设为默认
  const handleSetDefault = async (modelId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/models/${modelId}/set-default`, {
        method: 'POST',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (!res.ok) throw new Error('设置失败');
      
      message.success('已设为默认模型');
      loadModels();
    } catch (err) {
      message.error('设置失败');
    }
  };

  // 表格列定义
  const columns: ProColumns<ModelItem>[] = [
    {
      title: '模型',
      dataIndex: 'name',
      key: 'name',
      render: (_, record) => (
        <Space>
          <ApiOutlined style={{ color: '#FF6B35' }} />
          <Text strong>{record.name}</Text>
          {record.is_default && <Tag color="gold" icon={<CheckCircleFilled />}>默认</Tag>}
        </Space>
      ),
    },
    {
      title: '提供商',
      dataIndex: 'provider',
      key: 'provider',
      width: 120,
      render: (_, record) => {
        const info = providerMap[record.provider] || { text: record.provider, color: 'default' };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
    },
    {
      title: '模型名',
      dataIndex: 'model_name',
      key: 'model_name',
      width: 150,
      render: (val) => <Text code>{val || '-'}</Text>,
    },
    {
      title: 'API Key',
      dataIndex: 'api_key',
      key: 'api_key',
      width: 150,
      render: (val) => val || '-',
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      width: 80,
      render: (val) => val ? <Tag color="success">启用</Tag> : <Tag>禁用</Tag>,
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
      width: 200,
      render: (_, record) => (
        <Space>
          {!record.is_default && (
            <Button 
              type="link" 
              size="small"
              onClick={() => handleSetDefault(record.model_id)}
            >
              设为默认
            </Button>
          )}
          <ModalForm
            key="edit"
            title="编辑模型"
            trigger={
              <Button type="link" size="small" icon={<EditOutlined />}>
                编辑
              </Button>
            }
            onFinish={(values) => handleUpdate(record.model_id, values)}
          >
            <ProFormText
              name="name"
              label="显示名称"
              placeholder="如：我的GPT-4"
              initialValue={record.name}
            />
            {!record.api_key && (
              <ProFormText
                name="api_key"
                label="API Key"
                placeholder="请输入 API Key"
                rules={[{ required: true }]}
              />
            )}
            <ProFormText
              name="model_name"
              label="模型名称"
              placeholder="如：gpt-4o"
              initialValue={record.model_name}
            />
            <ProFormSwitch
              name="enabled"
              label="启用"
              initialValue={record.enabled}
            />
          </ModalForm>
          <Popconfirm
            title="确定删除此模型？"
            onConfirm={() => handleDelete(record.model_id)}
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

  // 提供商选项
  const providerOptions = Object.entries(providers).map(([key, value]: [string, any]) => ({
    label: value.name || key,
    value: key
  }));

  return (
    <div className={styles.modelsContainer}>
      <ProTable<ModelItem>
        actionRef={actionRef}
        columns={columns}
        dataSource={models}
        rowKey="model_id"
        loading={loading}
        search={false}
        pagination={{ pageSize: 10 }}
        toolBarRender={() => [
          <ModalForm
            key="create"
            title="添加模型配置"
            trigger={
              <Button type="primary" icon={<PlusOutlined />}>
                添加模型
              </Button>
            }
            onFinish={handleCreate}
          >
            <ProFormText
              name="name"
              label="显示名称"
              placeholder="如：我的GPT-4"
              rules={[{ required: true, message: '请输入显示名称' }]}
            />
            <ProFormSelect
              name="provider"
              label="模型提供商"
              options={providerOptions}
              rules={[{ required: true, message: '请选择提供商' }]}
            />
            <ProFormText
              name="api_key"
              label="API Key"
              placeholder="请输入 API Key"
              rules={[{ required: true, message: '请输入 API Key' }]}
            />
            <ProFormText
              name="model_name"
              label="模型名称"
              placeholder="如：gpt-4o、qwen-plus"
            />
            <ProFormSwitch
              name="is_default"
              label="设为默认"
              initialValue={false}
            />
          </ModalForm>,
          <Button 
            key="refresh" 
            onClick={loadModels}
            loading={loading}
          >
            刷新
          </Button>
        ]}
        headerTitle={
          <span>
            模型配置 | 当前租户: {getTenantId()} | 共 {models.length} 个模型
          </span>
        }
      />
    </div>
  );
}
