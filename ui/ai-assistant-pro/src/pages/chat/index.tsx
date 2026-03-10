import { useState, useRef, useEffect, useMemo } from 'react';
import { useSearchParams, history } from '@umijs/max';
import {
  Alert,
  Avatar,
  Button,
  Card,
  Empty,
  Input,
  List,
  Space,
  Spin,
  Tag,
  Typography,
  message as antdMessage,
} from 'antd';
import {
  ApiOutlined,
  AppstoreOutlined,
  ClearOutlined,
  GlobalOutlined,
  LinkOutlined,
  RobotOutlined,
  SendOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { ProList } from '@ant-design/pro-components';
import styles from './index.less';

const { Text, Link } = Typography;
const { TextArea } = Input;

type ToolStage = 'idle' | 'running' | 'done';

interface SourceItem {
  title: string;
  url?: string;
  type: 'web' | 'function' | 'system';
}

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatApiResponse {
  session_id: string;
  reply: string;
  timestamp: string;
}

const buildErrorText = (error: unknown) => {
  if (error instanceof Error) return error.message;
  return '请求失败，请稍后重试';
};

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [functionCallingStatus, setFunctionCallingStatus] = useState<ToolStage>('idle');
  const [webSearchStatus, setWebSearchStatus] = useState<ToolStage>('idle');
  const [activeTools, setActiveTools] = useState<string[]>([]);
  const [resultSources, setResultSources] = useState<SourceItem[]>([]);
  const [sessionId] = useState(() => `web-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const chatHistory = useMemo(() => {
    if (messages.length === 0) return [];
    return messages
      .filter((msg) => msg.role === 'user')
      .slice(-5)
      .reverse()
      .map((msg, index) => ({
        id: msg.id,
        title: msg.content.slice(0, 24),
        time: index === 0 ? '刚刚' : msg.timestamp.toLocaleTimeString(),
      }));
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    const template = searchParams.get('template');
    if (template) {
      setInputValue(template);
      history.replace('/chat');
      void handleSendWithContent(template);
    }
  }, [searchParams]);

  const getStageColor = (stage: ToolStage) => {
    if (stage === 'running') return 'processing';
    if (stage === 'done') return 'success';
    return 'default';
  };

  const getStageText = (stage: ToolStage) => {
    if (stage === 'running') return '执行中';
    if (stage === 'done') return '已完成';
    return '待触发';
  };

  const handleSendWithContent = async (rawContent: string) => {
    if (!rawContent.trim()) return;

    const content = rawContent.trim();
    const userMessage: MessageItem = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);
    setRequestError(null);

    const shouldUseFunction = /(调用|function|计算|天气|执行|查询日历)/i.test(content);
    const shouldUseWebSearch = /(搜索|web|最新|新闻|资料|官网|链接)/i.test(content);

    setFunctionCallingStatus(shouldUseFunction ? 'running' : 'idle');
    setWebSearchStatus(shouldUseWebSearch ? 'running' : 'idle');

    const tools: string[] = [];
    if (shouldUseFunction) tools.push('Function Calling');
    if (shouldUseWebSearch) tools.push('Web Search');
    setActiveTools(tools);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: content,
        }),
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = payload?.detail || '对话请求失败';
        throw new Error(detail);
      }

      const chatResponse = payload as ChatApiResponse;
      const assistantMessage: MessageItem = {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: chatResponse.reply || '未返回有效回复',
        timestamp: chatResponse.timestamp ? new Date(chatResponse.timestamp) : new Date(),
      };

      const sources: SourceItem[] = [];
      if (shouldUseWebSearch) {
        sources.push({ title: 'Web Search 已触发（后端判断）', type: 'web' });
      }
      if (shouldUseFunction) {
        sources.push({ title: 'Function Calling 已触发（后端判断）', type: 'function' });
      }
      if (sources.length === 0) {
        sources.push({ title: '基础对话模型响应', type: 'system' });
      }

      setMessages((prev) => [...prev, assistantMessage]);
      setResultSources(sources);
      if (shouldUseFunction) setFunctionCallingStatus('done');
      if (shouldUseWebSearch) setWebSearchStatus('done');
    } catch (error) {
      const errMsg = buildErrorText(error);
      setRequestError(errMsg);
      setFunctionCallingStatus('idle');
      setWebSearchStatus('idle');
      setResultSources([]);
      antdMessage.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => handleSendWithContent(inputValue);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h3>对话历史</h3>
          <Button type="text" icon={<ClearOutlined />} onClick={() => setMessages([])} />
        </div>
        <Button
          type="default"
          icon={<AppstoreOutlined />}
          className={styles.templateEntryButton}
          onClick={() => history.push('/templates')}
        >
          对话模板
        </Button>
        {chatHistory.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无历史" />
        ) : (
          <ProList
            dataSource={chatHistory}
            renderItem={(item) => (
              <div className={styles.historyItem}>
                <Text ellipsis>{item.title}</Text>
                <Text type="secondary" className={styles.time}>
                  {item.time}
                </Text>
              </div>
            )}
            metas={{ title: {}, description: {} }}
            split
            size="small"
          />
        )}
      </div>

      <div className={styles.chatMain}>
        <div className={styles.chatHeader}>
          <Space>
            <RobotOutlined style={{ fontSize: 20, color: '#FF6B35' }} />
            <span>AI 助手</span>
          </Space>
          <Button type="text" icon={<SettingOutlined />} />
        </div>

        <div className={styles.statusPanel}>
          <Card size="small" bordered={false}>
            <Space wrap>
              <Text type="secondary">能力状态</Text>
              <Tag icon={<ApiOutlined />} color={getStageColor(functionCallingStatus)}>
                Function Calling · {getStageText(functionCallingStatus)}
              </Tag>
              <Tag icon={<GlobalOutlined />} color={getStageColor(webSearchStatus)}>
                Web Search · {getStageText(webSearchStatus)}
              </Tag>
            </Space>
            {activeTools.length > 0 && (
              <Alert
                showIcon
                type="info"
                className={styles.toolAlert}
                message={`最近一次调用：${activeTools.join(' + ')}`}
              />
            )}

            <div className={styles.sourceBlock}>
              <Text type="secondary">结果来源列表</Text>
              {resultSources.length === 0 ? (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="暂无来源结果"
                  className={styles.sourceEmpty}
                />
              ) : (
                <List
                  size="small"
                  className={styles.sourceList}
                  dataSource={resultSources}
                  renderItem={(item) => (
                    <List.Item>
                      <Space size={8}>
                        <LinkOutlined />
                        {item.url ? (
                          <Link href={item.url} target="_blank">
                            {item.title}
                          </Link>
                        ) : (
                          <Text>{item.title}</Text>
                        )}
                        <Tag>{item.type === 'web' ? 'Web' : item.type === 'function' ? 'Function' : 'System'}</Tag>
                      </Space>
                    </List.Item>
                  )}
                />
              )}
            </div>
          </Card>
        </div>

        <div className={styles.messageList}>
          {requestError && (
            <Alert
              showIcon
              type="error"
              message={requestError}
              action={
                <Button type="link" size="small" onClick={() => setRequestError(null)}>
                  关闭
                </Button>
              }
            />
          )}

          {messages.length === 0 ? (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="开始与 AI 助手对话" />
          ) : (
            <List
              dataSource={messages}
              renderItem={(item) => (
                <div className={`${styles.messageItem} ${styles[item.role]}`}>
                  <Avatar
                    icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    className={styles.avatar}
                    style={{ backgroundColor: item.role === 'user' ? '#FF6B35' : '#1890ff' }}
                  />
                  <div className={styles.messageContent}>
                    <div className={styles.messageText}>{item.content}</div>
                    <div className={styles.messageTime}>{item.timestamp.toLocaleTimeString()}</div>
                  </div>
                </div>
              )}
            />
          )}
          {loading && (
            <div className={styles.loading}>
              <Spin tip="AI 正在思考..." />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputArea}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="输入消息，按 Enter 发送，Shift + Enter 换行"
            autoSize={{ minRows: 1, maxRows: 4 }}
            className={styles.textarea}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={() => void handleSend()}
            loading={loading}
            disabled={!inputValue.trim()}
            className={styles.sendButton}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  );
}
