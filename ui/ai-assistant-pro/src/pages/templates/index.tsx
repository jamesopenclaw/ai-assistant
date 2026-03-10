import { useEffect, useMemo, useState } from 'react';
import { history } from '@umijs/max';
import { Alert, Button, Card, Col, Empty, Input, Row, Select, Space, Spin, Tag, Typography } from 'antd';
import { BulbOutlined, SearchOutlined } from '@ant-design/icons';
import styles from './index.less';

const { Text, Paragraph } = Typography;
const { Search } = Input;

interface PromptTemplate {
  id: string;
  title: string;
  category: string;
  content: string;
}

interface TemplateApiItem {
  id: string;
  name: string;
  content: string;
}

const fallbackTemplates: PromptTemplate[] = [
  { id: 'fallback-1', title: '周报生成', category: '办公', content: '请根据以下本周工作记录，输出一份结构清晰的周报，包含：成果、风险、下周计划。' },
  { id: 'fallback-2', title: '代码评审建议', category: '研发', content: '请作为高级工程师评审以下代码，指出可读性、性能和安全性问题，并给出改进建议。' },
  { id: 'fallback-3', title: '会议纪要整理', category: '办公', content: '请将下面会议记录整理为会议纪要，包含：决策事项、待办列表、负责人、截止时间。' },
];

const inferCategory = (name: string) => {
  if (/代码|bug|架构/i.test(name)) return '研发';
  if (/会议|邮件|PRD/i.test(name)) return '办公';
  if (/学习|面试/i.test(name)) return '成长';
  return '通用';
};

export default function TemplatesPage() {
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);

  useEffect(() => {
    const loadTemplates = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/templates');
        const payload = await response.json().catch(() => null);
        if (!response.ok || !Array.isArray(payload)) {
          throw new Error(payload?.detail || '加载模板失败');
        }
        const normalized = (payload as TemplateApiItem[]).map((item) => ({
          id: item.id,
          title: item.name,
          category: inferCategory(item.name),
          content: item.content,
        }));
        setTemplates(normalized);
      } catch (err) {
        setTemplates(fallbackTemplates);
        setError(err instanceof Error ? err.message : '加载失败，已切换到本地模板');
      } finally {
        setLoading(false);
      }
    };

    void loadTemplates();
  }, []);

  const categories = useMemo(() => Array.from(new Set(templates.map((item) => item.category))), [templates]);

  const filteredTemplates = useMemo(
    () =>
      templates.filter((item) => {
        const matchCategory = category === 'all' || item.category === category;
        const lowerKeyword = keyword.trim().toLowerCase();
        const matchKeyword =
          !lowerKeyword ||
          item.title.toLowerCase().includes(lowerKeyword) ||
          item.content.toLowerCase().includes(lowerKeyword);
        return matchCategory && matchKeyword;
      }),
    [templates, keyword, category],
  );

  const handleUseTemplate = (template: PromptTemplate) => {
    history.push(`/chat?template=${encodeURIComponent(template.content)}`);
  };

  return (
    <div className={styles.templatesContainer}>
      <Card className={styles.headerCard} bordered={false}>
        <Space>
          <BulbOutlined className={styles.headerIcon} />
          <div>
            <h2>对话模板</h2>
            <Text type="secondary">支持按关键词和分类筛选，点击模板即可带入聊天页快速开始</Text>
          </div>
        </Space>
      </Card>

      {error && <Alert type="warning" showIcon message={`模板服务异常：${error}`} />}

      <Card className={styles.filterCard} bordered={false}>
        <Space wrap size={12} className={styles.filterBar}>
          <Search
            allowClear
            value={keyword}
            placeholder="搜索模板标题或内容"
            className={styles.searchInput}
            prefix={<SearchOutlined />}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <Select
            value={category}
            className={styles.categorySelect}
            onChange={setCategory}
            options={[
              { value: 'all', label: '全部分类' },
              ...categories.map((item) => ({ value: item, label: item })),
            ]}
          />
          <Text type="secondary">共 {filteredTemplates.length} 条结果</Text>
        </Space>
      </Card>

      {loading ? (
        <Card bordered={false}>
          <Spin tip="模板加载中..." />
        </Card>
      ) : filteredTemplates.length === 0 ? (
        <Card bordered={false}>
          <Empty description="没有匹配的模板，试试更换关键词或分类" image={Empty.PRESENTED_IMAGE_SIMPLE}>
            <Button
              onClick={() => {
                setKeyword('');
                setCategory('all');
              }}
            >
              清空筛选
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {filteredTemplates.map((item) => (
            <Col xs={24} sm={12} lg={8} xl={6} key={item.id}>
              <Card
                hoverable
                className={styles.templateCard}
                title={item.title}
                extra={<Tag color="blue">{item.category}</Tag>}
                actions={[
                  <Button type="link" key="use" onClick={() => handleUseTemplate(item)}>
                    使用模板
                  </Button>,
                ]}
              >
                <Paragraph ellipsis={{ rows: 3 }}>{item.content}</Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
