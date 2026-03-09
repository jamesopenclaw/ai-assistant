import { useState, useRef } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType, 
  ModalForm, 
  ProFormText, 
  ProFormSelect, 
  ProFormTextArea,
  ProDescriptions 
} from '@ant-design/pro-components';
import { 
  Button, 
  Space, 
  Tag, 
  Avatar, 
  Typography, 
  message, 
  Popconfirm,
  Dropdown 
} from 'antd';
import { 
  PlusOutlined, 
  FileTextOutlined, 
  FolderOutlined, 
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  EyeOutlined
} from '@ant-design/icons';
import type { KnowledgeItem } from './data.d';
import styles from './index.less';

const { Text, Paragraph } = Typography;

const categoryMap = {
  document: { text: '文档', color: 'blue' },
  code: { text: '代码', color: 'green' },
  api: { text: 'API', color: 'purple' },
  other: { text: '其他', color: 'default' },
};

// 模拟数据
const mockData: KnowledgeItem[] = [
  {
    id: '1',
    title: 'React Hooks 最佳实践',
    category: 'document',
    tags: ['React', 'Hooks', '前端'],
    content: '详细介绍了 React Hooks 的使用规范和最佳实践...',
    author: 'Linus',
    createdAt: '2026-03-01 10:00:00',
    updatedAt: '2026-03-09 15:30:00',
    views: 1250,
    status: 'published',
  },
  {
    id: '2',
    title: 'Python 爬虫实现指南',
    category: 'code',
    tags: ['Python', '爬虫', '数据采集'],
    content: '使用 requests 和 BeautifulSoup 实现网页爬取...',
    author: 'Bob',
    createdAt: '2026-02-28 14:00:00',
    updatedAt: '2026-03-08 09:00:00',
    views: 890,
    status: 'published',
  },
  {
    id: '3',
    title: 'RESTful API 设计规范',
    category: 'api',
    tags: ['API', 'REST', '后端'],
    content: '详细说明了 RESTful API 的设计原则和最佳实践...',
    author: 'Alice',
    createdAt: '2026-02-25 11:00:00',
    updatedAt: '2026-03-07 16:00:00',
    views: 2100,
    status: 'published',
  },
  {
    id: '4',
    title: '数据库优化技巧',
    category: 'document',
    tags: ['数据库', 'MySQL', '优化'],
    content: '分享数据库性能优化的经验和方法...',
    author: 'Linus',
    createdAt: '2026-03-05 09:00:00',
    updatedAt: '2026-03-09 10:00:00',
    views: 560,
    status: 'draft',
  },
];

export default function KnowledgePage() {
  const actionRef = useRef<ActionType>();

  const handleEdit = (record: KnowledgeItem) => {
    message.info(`编辑知识: ${record.title}`);
  };

  const handleDelete = (record: KnowledgeItem) => {
    message.success(`删除知识: ${record.title}`);
    actionRef.current?.reload();
  };

  const handleView = (record: KnowledgeItem) => {
    message.info(`查看知识: ${record.title}`);
  };

  const handleShare = (record: KnowledgeItem) => {
    message.success(`分享链接已复制: ${record.title}`);
  };

  const handleDownload = (record: KnowledgeItem) => {
    message.success(`下载知识: ${record.title}`);
  };

  const expandedRowRender = (record: KnowledgeItem) => (
    <div className={styles.expandedContent}>
      <ProDescriptions column={2} size="small">
        <ProDescriptions.Item label="内容摘要">
          {record.content.substring(0, 100)}...
        </ProDescriptions.Item>
        <ProDescriptions.Item label="标签">
          <Space wrap>
            {record.tags.map((tag) => (
              <Tag key={tag} color="blue">{tag}</Tag>
            ))}
          </Space>
        </ProDescriptions.Item>
      </ProDescriptions>
    </div>
  );

  const columns: ProColumns<KnowledgeItem>[] = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (_, record) => (
        <Space>
          <Avatar 
            size="small" 
            icon={record.category === 'folder' ? <FolderOutlined /> : <FileTextOutlined />}
            style={{ 
              backgroundColor: categoryMap[record.category as keyof typeof categoryMap]?.color === 'blue' ? '#1890ff' :
                             categoryMap[record.category as keyof typeof categoryMap]?.color === 'green' ? '#52c41a' :
                             categoryMap[record.category as keyof typeof categoryMap]?.color === 'purple' ? '#722ed1' : '#d9d9d9'
            }}
          />
          <Text strong>{record.title}</Text>
        </Space>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      valueType: 'select',
      valueEnum: {
        document: { text: '文档', status: 'Default' },
        code: { text: '代码', status: 'Success' },
        api: { text: 'API', status: 'Processing' },
        other: { text: '其他', status: 'Default' },
      },
      render: (_, record) => {
        const category = categoryMap[record.category as keyof typeof categoryMap];
        return <Tag color={category?.color}>{category?.text}</Tag>;
      },
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags) => (
        <Space wrap size="small">
          {tags?.map((tag: string) => (
            <Tag key={tag}>{tag}</Tag>
          ))}
        </Space>
      ),
      search: false,
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      render: (author) => (
        <Space>
          <Avatar size="small" src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${author}`} />
          {author}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      valueType: 'select',
      valueEnum: {
        published: { text: '已发布', status: 'Success' },
        draft: { text: '草稿', status: 'Warning' },
      },
    },
    {
      title: '浏览量',
      dataIndex: 'views',
      key: 'views',
      sorter: (a, b) => a.views - b.views,
      search: false,
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      valueType: 'dateTime',
      sorter: (a, b) => new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime(),
      search: false,
    },
    {
      title: '操作',
      key: 'action',
      valueType: 'option',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Dropdown
            menu={{
              items: [
                {
                  key: 'share',
                  label: '分享',
                  icon: <ShareAltOutlined />,
                  onClick: () => handleShare(record),
                },
                {
                  key: 'download',
                  label: '下载',
                  icon: <DownloadOutlined />,
                  onClick: () => handleDownload(record),
                },
                {
                  type: 'divider',
                },
                {
                  key: 'delete',
                  label: '删除',
                  icon: <DeleteOutlined />,
                  danger: true,
                  onClick: () => handleDelete(record),
                },
              ],
            }}
          >
            <Button type="link" size="small" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.knowledgeContainer}>
      <ProTable<KnowledgeItem>
        actionRef={actionRef}
        columns={columns}
        dataSource={mockData}
        rowKey="id"
        search={{
          labelWidth: 'auto',
        }}
        expandable={{
          expandedRowRender,
          rowExpandable: (record) => true,
        }}
        toolBarRender={() => [
          <ModalForm
            key="create"
            title="创建知识条目"
            trigger={
              <Button type="primary" icon={<PlusOutlined />}>
                新建知识
              </Button>
            }
            onFinish={async (values) => {
              message.success('创建成功');
              return true;
            }}
          >
            <ProFormText
              name="title"
              label="标题"
              placeholder="请输入知识标题"
              rules={[{ required: true }]}
            />
            <ProFormSelect
              name="category"
              label="分类"
              placeholder="请选择分类"
              options={[
                { label: '文档', value: 'document' },
                { label: '代码', value: 'code' },
                { label: 'API', value: 'api' },
                { label: '其他', value: 'other' },
              ]}
              rules={[{ required: true }]}
            />
            <ProFormText
              name="tags"
              label="标签"
              placeholder="请输入标签，用逗号分隔"
            />
            <ProFormTextArea
              name="content"
              label="内容"
              placeholder="请输入知识内容"
              rules={[{ required: true }]}
              fieldProps={{
                rows: 4,
              }}
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
