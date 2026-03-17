import { useState, useRef, useEffect } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType,
  Card,
  Tag,
  Button,
  Space,
  Modal,
  Input,
  message,
  Badge,
  Avatar,
  Divider
} from 'antd';
import { 
  UserOutlined, 
  PhoneOutlined, 
  ApiOutlined,
  SwapOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import styles from './index.less';

const { Text, Paragraph } = Typography = require('antd').Typography;
const { Search } = Input;

// 获取租户 ID
const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

interface Agent {
  agent_id: string;
  name: string;
  status: string;
  tenant_id: number;
  last_active: string;
}

interface SessionStatus {
  session_id: string;
  mode: string;  // ai, human, waiting
  agent_id?: string;
  agent_name?: string;
  message?: string;
}

export default function CustomerServicePage() {
  const actionRef = useRef<ActionType>();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null);
  const [currentSession, setCurrentSession] = useState<string>('web-session-' + Date.now());
  const [loading, setLoading] = useState(false);
  const [transferModalVisible, setTransferModalVisible] = useState(false);

  // 加载客服列表
  const loadAgents = async () => {
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/customer-service/agents', {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = await res.json();
      setAgents(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('加载客服失败:', err);
    }
  };

  // 获取当前会话状态
  const loadSessionStatus = async () => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/customer-service/status/${currentSession}`, {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = await res.json();
      setSessionStatus(data);
    } catch (err) {
      console.error('获取状态失败:', err);
    }
  };

  useEffect(() => {
    loadAgents();
    loadSessionStatus();
    const interval = setInterval(loadAgents, 5000); // 每5秒刷新
    return () => clearInterval(interval);
  }, []);

  // 客服上线
  const handleAgentOnline = async (name: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/customer-service/agents', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({ name })
      });
      
      if (res.ok) {
        message.success('客服已上线');
        loadAgents();
      }
    } catch (err) {
      message.error('上线失败');
    }
  };

  // 客服下线
  const handleAgentOffline = async (agentId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/customer-service/agents/${agentId}`, {
        method: 'DELETE',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (res.ok) {
        message.success('客服已下线');
        loadAgents();
      }
    } catch (err) {
      message.error('下线失败');
    }
  };

  // 转人工
  const handleTransferToHuman = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/customer-service/transfer', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({ session_id: currentSession })
      });
      
      const data = await res.json();
      message.info(data.message || '转接成功');
      loadSessionStatus();
    } catch (err) {
      message.error('转接失败');
    } finally {
      setLoading(false);
    }
  };

  // 转回AI
  const handleTransferToAI = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/customer-service/transfer-to-ai', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId 
        },
        body: JSON.stringify({ session_id: currentSession })
      });
      
      const data = await res.json();
      message.info(data.message || '已切换回AI');
      loadSessionStatus();
    } catch (err) {
      message.error('切换失败');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'success';
      case 'busy': return 'warning';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return '在线';
      case 'busy': return '忙碌';
      default: return '离线';
    }
  };

  const getModeTag = (mode: string) => {
    switch (mode) {
      case 'ai': return <Tag color="blue" icon={<ApiOutlined />}>AI 客服</Tag>;
      case 'human': return <Tag color="green" icon={<UserOutlined />}>人工客服</Tag>;
      case 'waiting': return <Tag color="orange" icon={<SwapOutlined />}>等待分配</Tag>;
      default: return <Tag>{mode}</Tag>;
    }
  };

  const columns: ProColumns<Agent>[] = [
    {
      title: '客服',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} style={{ backgroundColor: record.status === 'online' ? '#52c41a' : '#d9d9d9' }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Badge status={getStatusColor(status)} text={getStatusText(status)} />
      ),
    },
    {
      title: '最后活跃',
      dataIndex: 'last_active',
      key: 'last_active',
      width: 180,
      render: (val) => val ? new Date(val).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button 
          type="link" 
          danger 
          size="small"
          onClick={() => handleAgentOffline(record.agent_id)}
        >
          下线
        </Button>
      ),
    },
  ];

  return (
    <div className={styles.csContainer}>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 当前会话状态 */}
        <Card title="当前会话状态" extra={getModeTag(sessionStatus?.mode || 'ai')}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text type="secondary">会话ID：</Text>
              <Text code>{currentSession}</Text>
            </div>
            
            {sessionStatus?.mode === 'human' && (
              <div>
                <Text type="secondary">当前客服：</Text>
                <Tag color="green">{sessionStatus.agent_name || sessionStatus.agent_id}</Tag>
              </div>
            )}
            
            <Divider />
            
            <Space>
              {sessionStatus?.mode === 'ai' ? (
                <Button 
                  type="primary" 
                  icon={<SwapOutlined />}
                  onClick={handleTransferToHuman}
                  loading={loading}
                >
                  转人工客服
                </Button>
              ) : (
                <Button 
                  icon={<ApiOutlined />}
                  onClick={handleTransferToAI}
                  loading={loading}
                >
                  转回 AI
                </Button>
              )}
            </Space>
          </Space>
        </Card>

        {/* 在线客服列表 */}
        <Card 
          title="在线客服" 
          extra={
            <Button 
              type="primary" 
              size="small"
              onClick={() => handleAgentOnline('客服' + Math.floor(Math.random() * 100))}
            >
              客服上线
            </Button>
          }
        >
          <ProTable<Agent>
            actionRef={actionRef}
            columns={columns}
            dataSource={agents}
            rowKey="agent_id"
            pagination={false}
            search={false}
            toolBarRender={false}
          />
        </Card>
      </Space>
    </div>
  );
}
