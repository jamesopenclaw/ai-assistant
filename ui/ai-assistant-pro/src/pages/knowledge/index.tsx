import { useState, useRef, useEffect } from 'react';
import { 
  ProTable, 
  ProColumns, 
  ActionType, 
  ModalForm, 
  ProFormText, 
  ProDescriptions
} from '@ant-design/pro-components';
import { 
  Button, 
  Space, 
  Tag, 
  Typography, 
  message, 
  Card,
  Upload
} from 'antd';
import { 
  PlusOutlined, 
  FileTextOutlined,
  DeleteOutlined,
  InboxOutlined
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import styles from './index.less';

const { Text } = Typography;
const { Dragger } = Upload;

// 文档类型映射
const fileTypeMap: Record<string, { text: string; color: string }> = {
  pdf: { text: 'PDF', color: 'red' },
  doc: { text: 'Word', color: 'blue' },
  docx: { text: 'Word', color: 'blue' },
  txt: { text: '文本', color: 'default' },
  md: { text: 'Markdown', color: 'orange' },
};

// 获取租户 ID
const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

interface KnowledgeDoc {
  id: string;
  filename: string;
  file_type: string;
  uploaded_at: string;
  chunk_count: number;
}

export default function KnowledgePage() {
  const actionRef = useRef<ActionType>();
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  // 加载文档列表
  const loadDocs = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const res = await fetch('/api/knowledge/list', {
        headers: { 'X-Tenant-ID': tenantId }
      });
      const data = await res.json();
      setDocs(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('加载文档失败:', err);
      message.error('加载文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  // 上传文档
  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options;
    setUploading(true);
    
    try {
      const tenantId = getTenantId();
      const formData = new FormData();
      formData.append('file', file as File);
      
      const res = await fetch('/api/knowledge/add', {
        method: 'POST',
        headers: { 'X-Tenant-ID': tenantId },
        body: formData
      });
      
      if (!res.ok) throw new Error('上传失败');
      
      const result = await res.json();
      message.success(`${file.name} 上传成功`);
      loadDocs();
      onSuccess?.(result);
    } catch (err) {
      message.error(`${file.name} 上传失败`);
      onError?.(err as Error);
    } finally {
      setUploading(false);
    }
  };

  // 删除文档
  const handleDelete = async (docId: string) => {
    try {
      const tenantId = getTenantId();
      const res = await fetch(`/api/knowledge/${docId}`, {
        method: 'DELETE',
        headers: { 'X-Tenant-ID': tenantId }
      });
      
      if (!res.ok) throw new Error('删除失败');
      
      message.success('删除成功');
      loadDocs();
    } catch (err) {
      message.error('删除失败');
    }
  };

  // 表格列定义
  const columns: ProColumns<KnowledgeDoc>[] = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      render: (_, record) => (
        <Space>
          <FileTextOutlined style={{ color: '#FF6B35' }} />
          <Text strong>{record.filename}</Text>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 100,
      render: (_, record) => {
        const info = fileTypeMap[record.file_type.toLowerCase()] || { text: record.file_type, color: 'default' };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
    },
    {
      title: 'Chunk 数量',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 120,
      render: (count) => <Tag color="blue">{count} 个片段</Tag>,
    },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
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
          icon={<DeleteOutlined />}
          onClick={() => handleDelete(record.id)}
        >
          删除
        </Button>
      ),
    },
  ];

  return (
    <div className={styles.knowledgeContainer}>
      <Spin spinning={loading}>
        <Card 
          title="知识库文档" 
          extra={
            <span style={{ color: '#666', fontSize: 12 }}>
              共 {docs.length} 个文档 | 当前租户: {getTenantId()}
            </span>
          }
        >
          {/* 上传区域 */}
          <div style={{ marginBottom: 16 }}>
            <Dragger
              name="file"
              multiple={false}
              customRequest={handleUpload}
              showUploadList={false}
              accept=".pdf,.doc,.docx,.txt,.md"
              disabled={uploading}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined style={{ color: '#FF6B35', fontSize: 48 }} />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
              <p className="ant-upload-hint">
                支持 PDF、Word、TXT、Markdown 格式
              </p>
            </Dragger>
          </div>

          {/* 文档列表 */}
          <ProTable<KnowledgeDoc>
            actionRef={actionRef}
            columns={columns}
            dataSource={docs}
            rowKey="id"
            search={false}
            pagination={{ pageSize: 10 }}
            toolBarRender={() => [
              <Button 
                key="refresh" 
                onClick={loadDocs}
                loading={loading}
              >
                刷新
              </Button>
            ]}
          />
        </Card>
      </Spin>
    </div>
  );
}
