import { useRef } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType, 
  ModalForm, 
  ProFormText, 
  ProFormSelect, 
  ProFormDateTimePicker,
  ProFormDigit 
} from '@ant-design/pro-components';
import { 
  Button, 
  Space, 
  Tag, 
  Avatar, 
  Typography, 
  message, 
  Popconfirm, 
  Badge 
} from 'antd';
import { 
  PlusOutlined, 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  SyncOutlined, 
  DeleteOutlined, 
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import type { PIPipeline } from './data.d';
import styles from './index.less';

const { Text } = Typography;

const statusMap = {
  success: { text: '成功', color: 'success' },
  failed: { text: '失败', color: 'error' },
  running: { text: '运行中', color: 'processing' },
  pending: { text: '等待中', color: 'default' },
  cancelled: { text: '已取消', color: 'default' },
};

// 模拟数据
const mockData: PIPipeline[] = [
  {
    id: '1',
    name: 'frontend-build',
    repo: 'ai-assistant',
    branch: 'main',
    status: 'success',
    trigger: 'push',
    lastRun: '2026-03-09 10:30:00',
    duration: '5m 32s',
    author: 'Linus',
    commit: 'feat: add new feature',
  },
  {
    id: '2',
    name: 'backend-test',
    repo: 'ai-assistant',
    branch: 'develop',
    status: 'running',
    trigger: 'manual',
    lastRun: '2026-03-09 11:00:00',
    duration: '2m 15s',
    author: 'Bob',
    commit: 'fix: bug fix',
  },
  {
    id: '3',
    name: 'deploy-prod',
    repo: 'ai-assistant',
    branch: 'main',
    status: 'failed',
    trigger: 'schedule',
    lastRun: '2026-03-09 09:00:00',
    duration: '1m 45s',
    author: 'Alice',
    commit: 'chore: update config',
  },
  {
    id: '4',
    name: 'security-scan',
    repo: 'ai-assistant',
    branch: 'main',
    status: 'pending',
    trigger: 'push',
    lastRun: '2026-03-08 22:00:00',
    duration: '-',
    author: 'System',
    commit: 'security: scan results',
  },
];

export default function CICDPage() {
  const actionRef = useRef<ActionType>();

  const handleRun = (record: PIPipeline) => {
    message.success(`触发流水线: ${record.name}`);
  };

  const handleStop = (record: PIPipeline) => {
    message.warning(`停止流水线: ${record.name}`);
  };

  const handleEdit = (record: PIPipeline) => {
    message.info(`编辑流水线: ${record.name}`);
  };

  const handleDelete = (record: PIPipeline) => {
    message.success(`删除流水线: ${record.name}`);
    actionRef.current?.reload();
  };

  const columns: ProColumns<PIPipeline>[] = [
    {
      title: '流水线名称',
      dataIndex: 'name',
      key: 'name',
      render: (_, record) => (
        <Space>
          <Avatar 
            size="small" 
            style={{ 
              backgroundColor: record.status === 'success' ? '#52c41a' : 
                             record.status === 'failed' ? '#f5222d' : 
                             record.status === 'running' ? '#1890ff' : '#d9d9d9' 
            }}
            icon={record.status === 'running' ? <SyncOutlined spin /> : undefined}
          />
          <Text strong>{record.name}</Text>
        </Space>
      ),
    },
    {
      title: '仓库',
      dataIndex: 'repo',
      key: 'repo',
      ellipsis: true,
    },
    {
      title: '分支',
      dataIndex: 'branch',
      key: 'branch',
      render: (branch) => <Tag color="blue">{branch}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      valueType: 'select',
      valueEnum: {
        success: { text: '成功', status: 'Success' },
        failed: { text: '失败', status: 'Error' },
        running: { text: '运行中', status: 'Processing' },
        pending: { text: '等待中', status: 'Default' },
        cancelled: { text: '已取消', status: 'Default' },
      },
      render: (_, record) => {
        const status = statusMap[record.status as keyof typeof statusMap];
        return (
          <Badge 
            status={status.color as any} 
            text={status.text} 
          />
        );
      },
    },
    {
      title: '触发方式',
      dataIndex: 'trigger',
      key: 'trigger',
      valueType: 'select',
      valueEnum: {
        push: { text: '代码推送' },
        pull_request: { text: '合并请求' },
        manual: { text: '手动触发' },
        schedule: { text: '定时任务' },
      },
    },
    {
      title: '运行时长',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: '最近运行',
      dataIndex: 'lastRun',
      key: 'lastRun',
      valueType: 'dateTime',
    },
    {
      title: '提交信息',
      dataIndex: 'commit',
      key: 'commit',
      ellipsis: true,
      render: (commit) => (
        <Text type="secondary" ellipsis style={{ maxWidth: 200 }}>
          {commit}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      valueType: 'option',
      render: (_, record) => (
        <Space size="middle">
          {record.status === 'running' ? (
            <Button
              type="link"
              icon={<PauseCircleOutlined />}
              onClick={() => handleStop(record)}
            >
              停止
            </Button>
          ) : (
            <Button
              type="link"
              icon={<PlayCircleOutlined />}
              onClick={() => handleRun(record)}
            >
              运行
            </Button>
          )}
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此流水线吗？"
            onConfirm={() => handleDelete(record)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.cicdContainer}>
      <ProTable<PIPipeline>
        actionRef={actionRef}
        columns={columns}
        dataSource={mockData}
        rowKey="id"
        search={false}
        toolBarRender={() => [
          <ModalForm
            key="create"
            title="创建流水线"
            trigger={
              <Button type="primary" icon={<PlusOutlined />}>
                新建流水线
              </Button>
            }
            onFinish={async (values) => {
              message.success('创建成功');
              return true;
            }}
          >
            <ProFormText
              name="name"
              label="流水线名称"
              placeholder="请输入流水线名称"
              rules={[{ required: true }]}
            />
            <ProFormText
              name="repo"
              label="仓库"
              placeholder="请输入仓库名称"
              rules={[{ required: true }]}
            />
            <ProFormSelect
              name="branch"
              label="分支"
              placeholder="请选择分支"
              options={[
                { label: 'main', value: 'main' },
                { label: 'develop', value: 'develop' },
                { label: 'feature/*', value: 'feature' },
              ]}
              rules={[{ required: true }]}
            />
            <ProFormSelect
              name="trigger"
              label="触发方式"
              placeholder="请选择触发方式"
              options={[
                { label: '代码推送', value: 'push' },
                { label: '合并请求', value: 'pull_request' },
                { label: '手动触发', value: 'manual' },
                { label: '定时任务', value: 'schedule' },
              ]}
              rules={[{ required: true }]}
            />
          </ModalForm>,
        ]}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />
    </div>
  );
}
