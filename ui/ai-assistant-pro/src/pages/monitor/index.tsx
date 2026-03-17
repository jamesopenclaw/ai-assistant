import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Select, Space, Typography, Timeline } from 'antd';
import { 
  LineChartOutlined, 
  AlertOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  ApiOutlined 
} from '@ant-design/icons';

const { Text, Title } = Typography;

const getTenantId = () => localStorage.getItem('currentTenantId') || '1';

export default function MonitorPage() {
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [errors, setErrors] = useState<any[]>([]);
  const [performance, setPerformance] = useState<any[]>([]);
  const [hours, setHours] = useState(24);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      const headers = { 'X-Tenant-ID': tenantId };
      
      const [statsRes, logsRes, errorsRes, perfRes] = await Promise.all([
        fetch(`/api/monitor/stats?hours=${hours}`, { headers }),
        fetch(`/api/monitor/logs?hours=${hours}&limit=20`, { headers }),
        fetch(`/api/monitor/errors?hours=${hours}&limit=20`, { headers }),
        fetch(`/api/monitor/performance?hours=${hours}`, { headers })
      ]);
      
      setStats(await statsRes.json());
      setLogs(await logsRes.json());
      setErrors(await errorsRes.json());
      setPerformance(await perfRes.json());
    } catch (err) {
      console.error('加载监控数据失败:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, [hours]);

  const logColumns = [
    { title: '时间', dataIndex: 'timestamp', key: 'timestamp', width: 180,
      render: (val: string) => new Date(val).toLocaleString() },
    { title: '方法', dataIndex: 'method', key: 'method', width: 80,
      render: (v: string) => <Tag color={v === 'GET' ? 'blue' : v === 'POST' ? 'green' : 'orange'}>{v}</Tag> },
    { title: '路径', dataIndex: 'path', key: 'path', ellipsis: true },
    { title: '状态', dataIndex: 'status_code', key: 'status_code', width: 80,
      render: (v: number) => v < 400 ? <Tag color="success">{v}</Tag> : <Tag color="error">{v}</Tag> },
    { title: '耗时', dataIndex: 'duration_ms', key: 'duration_ms', width: 100,
      render: (v: number) => `${v.toFixed(0)}ms` },
  ];

  const perfColumns = [
    { title: '接口', dataIndex: 'endpoint', key: 'endpoint', ellipsis: true },
    { title: '请求数', dataIndex: 'request_count', key: 'request_count', width: 100 },
    { title: '错误数', dataIndex: 'error_count', key: 'error_count', width: 80,
      render: (v: number) => v > 0 ? <Tag color="error">{v}</Tag> : <Tag>0</Tag> },
    { title: '平均耗时', dataIndex: 'avg_duration_ms', key: 'avg_duration_ms', width: 100,
      render: (v: number) => `${v.toFixed(0)}ms` },
    { title: '最大耗时', dataIndex: 'max_duration_ms', key: 'max_duration_ms', width: 100,
      render: (v: number) => `${v.toFixed(0)}ms` },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select value={hours} onChange={setHours} style={{ width: 120 }}>
          <Select.Option value={1}>最近1小时</Select.Option>
          <Select.Option value={6}>最近6小时</Select.Option>
          <Select.Option value={24}>最近24小时</Select.Option>
          <Select.Option value={72}>最近3天</Select.Option>
        </Select>
      </Space>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总请求数"
              value={stats?.total_requests || 0}
              prefix={<ApiOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误数"
              value={stats?.total_errors || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: stats?.total_errors > 0 ? '#ff4d4f' : undefined }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误率"
              value={stats?.error_rate || 0}
              suffix="%"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均响应时间"
              value={stats?.avg_response_time_ms || 0}
              suffix="ms"
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="性能监控" loading={loading}>
            <Table
              dataSource={performance}
              columns={perfColumns}
              rowKey="endpoint"
              size="small"
              pagination={false}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="最近错误" loading={loading}>
            <Table
              dataSource={errors}
              columns={[
                { title: '时间', dataIndex: 'timestamp', key: 'timestamp', width: 160,
                  render: (val: string) => new Date(val).toLocaleString() },
                { title: '类型', dataIndex: 'error_type', key: 'error_type',
                  render: (v: string) => <Tag color="error">{v}</Tag> },
                { title: '消息', dataIndex: 'message', key: 'message', ellipsis: true },
              ]}
              rowKey="id"
              size="small"
              pagination={false}
            />
          </Card>
        </Col>
      </Row>

      <Card title="请求日志" style={{ marginTop: 16 }} loading={loading}>
        <Table
          dataSource={logs}
          columns={logColumns}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}
