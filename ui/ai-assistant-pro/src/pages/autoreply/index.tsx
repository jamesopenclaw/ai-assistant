import { useState, useRef, useEffect } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType,
  ModalForm,
  ProFormText,
  ProFormSelect,
  ProFormDigit
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
  ApiOutlined
} from '@ant-design/icons';
import styles from './index.less';

const { Text } = Typography;

// 获取租户 ID
const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

interface RuleItem {
  id: string;
  keywords: string[];
  reply: string;
  match_type: string;
  enabled: boolean;
  priority: number;
  created_at: string;
}

const matchTypeMap: Record<string, { text: string; color: string }> = {
  exact: { text: '精确匹配', color: 'blue' },
  fuzzy: { text: '模糊匹配', color: 'green' },
  regex: { text: '正则匹配', color: 'purple' },
};

export default function AutoreplyPage() {
  const actionRef = useRef<ActionType>();
  const [rules, setRules] = useState<RuleItem[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载规则列表
  const loadRules = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/autoreply/rules', {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = await res.json();
      setRules(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('加载规则失败:', err);
      message.error('加载规则列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  // 创建规则
  const handleCreate = async (values: any) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/autoreply/rules', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({
          keywords: values.keywords.split(/[,，]/).map((k: string) => k.trim()).filter(Boolean),
          reply: values.reply,
          match_type: values.match_type,
          priority: values.priority || 0
        })
      });
      
      if (!res.ok) throw new Error('创建失败');
      
      message.success('创建成功');
      loadRules();
      return true;
    } catch (err) {
      message.error('创建失败');
      return false;
    }
  };

  // 更新规则
  const handleUpdate = async (ruleId: string, values: any) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/autoreply/rules/${ruleId}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({
          keywords: values.keywords?.split(/[,，]/).map((k: string) => k.trim()).filter(Boolean),
          reply: values.reply,
          match_type: values.match_type,
          priority: values.priority
        })
      });
      
      if (!res.ok) throw new Error('更新失败');
      
      message.success('更新成功');
      loadRules();
      return true;
    } catch (err) {
      message.error('更新失败');
      return false;
    }
  };

  // 删除规则
  const handleDelete = async (ruleId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/autoreply/rules/${ruleId}`, {
        method: 'DELETE',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (!res.ok) throw new Error('删除失败');
      
      message.success('删除成功');
      loadRules();
    } catch (err) {
      message.error('删除失败');
    }
  };

  // 切换启用状态
  const handleToggle = async (rule: RuleItem) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/autoreply/rules/${rule.id}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({ enabled: !rule.enabled })
      });
      
      if (!res.ok) throw new Error('更新失败');
      
      message.success(rule.enabled ? '已禁用' : '已启用');
      loadRules();
    } catch (err) {
      message.error('操作失败');
    }
  };

  // 表格列定义
  const columns: ProColumns<RuleItem>[] = [
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (_, record) => (
        <Space wrap>
          {record.keywords.slice(0, 3).map((k: string) => (
            <Tag key={k} color="orange">{k}</Tag>
          ))}
          {record.keywords.length > 3 && <Tag>+{record.keywords.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: '回复内容',
      dataIndex: 'reply',
      key: 'reply',
      width: 200,
      render: (val) => (
        <Text ellipsis={{ tooltip: val }} style={{ maxWidth: 200 }}>
          {val}
        </Text>
      ),
    },
    {
      title: '匹配方式',
      dataIndex: 'match_type',
      key: 'match_type',
      width: 100,
      render: (_, record) => {
        const info = matchTypeMap[record.match_type] || { text: record.match_type, color: 'default' };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
      valueType: 'select',
      valueEnum: {
        exact: { text: '精确匹配', status: 'Success' },
        fuzzy: { text: '模糊匹配', status: 'Processing' },
        regex: { text: '正则匹配', status: 'Warning' },
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      sorter: (a, b) => a.priority - b.priority,
    },
    {
      title: '状态',
      dataIndex: 'enabled',
      key: 'enabled',
      width: 80,
      render: (_, record) => (
        <Switch 
          checked={record.enabled} 
          onChange={() => handleToggle(record)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val) => val ? new Date(val).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <ModalForm
            key="edit"
            title="编辑规则"
            trigger={
              <Button type="link" size="small" icon={<EditOutlined />}>
                编辑
              </Button>
            }
            onFinish={(values) => handleUpdate(record.id, values)}
          >
            <ProFormText
              name="keywords"
              label="关键词"
              placeholder="多个关键词用逗号分隔"
              initialValue={record.keywords.join(', ')}
              rules={[{ required: true, message: '请输入关键词' }]}
            />
            <ProFormText
              name="reply"
              label="回复内容"
              placeholder="请输入回复内容"
              initialValue={record.reply}
              rules={[{ required: true, message: '请输入回复内容' }]}
            />
            <ProFormSelect
              name="match_type"
              label="匹配方式"
              initialValue={record.match_type}
              options={[
                { label: '精确匹配', value: 'exact' },
                { label: '模糊匹配', value: 'fuzzy' },
                { label: '正则匹配', value: 'regex' },
              ]}
            />
            <ProFormDigit
              name="priority"
              label="优先级"
              placeholder="数字越大越优先"
              initialValue={record.priority}
              min={0}
              max={100}
            />
          </ModalForm>
          <Popconfirm
            title="确定删除此规则？"
            onConfirm={() => handleDelete(record.id)}
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
    <div className={styles.autoreplyContainer}>
      <ProTable<RuleItem>
        actionRef={actionRef}
        columns={columns}
        dataSource={rules}
        rowKey="id"
        loading={loading}
        search={false}
        pagination={{ pageSize: 10 }}
        toolBarRender={() => [
          <ModalForm
            key="create"
            title="创建关键词规则"
            trigger={
              <Button type="primary" icon={<PlusOutlined />}>
                新建规则
              </Button>
            }
            onFinish={handleCreate}
          >
            <ProFormText
              name="keywords"
              label="关键词"
              placeholder="多个关键词用逗号分隔"
              rules={[{ required: true, message: '请输入关键词' }]}
            />
            <ProFormText
              name="reply"
              label="回复内容"
              placeholder="请输入回复内容"
              rules={[{ required: true, message: '请输入回复内容' }]}
            />
            <ProFormSelect
              name="match_type"
              label="匹配方式"
              initialValue="fuzzy"
              options={[
                { label: '精确匹配', value: 'exact' },
                { label: '模糊匹配', value: 'fuzzy' },
                { label: '正则匹配', value: 'regex' },
              ]}
            />
            <ProFormDigit
              name="priority"
              label="优先级"
              placeholder="数字越大越优先"
              initialValue={0}
              min={0}
              max={100}
            />
          </ModalForm>,
          <Button 
            key="refresh" 
            onClick={loadRules}
            loading={loading}
          >
            刷新
          </Button>
        ]}
        headerTitle={
          <span>
            关键词自动回复 | 当前租户: {getTenantId()} | 共 {rules.length} 条规则
          </span>
        }
      />
    </div>
  );
}
