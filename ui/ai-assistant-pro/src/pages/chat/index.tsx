import { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, Avatar, List, Spin, Empty, Space, Typography } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined, SettingOutlined } from '@ant-design/icons';
import type { ProColumns } from '@ant-design/pro-components';
import { ProList } from '@ant-design/pro-components';
import styles from './index.less';

const { Text } = Typography;
const { TextArea } = Input;

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 模拟历史对话列表
  const chatHistory = [
    { id: '1', title: '关于 React Hooks 的问题', time: '10:30' },
    { id: '2', title: 'Python 爬虫实现', time: '昨天' },
    { id: '3', title: '数据库优化建议', time: '2天前' },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    // 模拟 AI 响应
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `收到您的问题：${inputValue}\n\n这是一个基于 Ant Design Pro 构建的 AI 助手界面。我可以帮助您解答问题、提供建议或进行代码审查。`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className={styles.chatContainer}>
      {/* 左侧历史记录 */}
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h3>对话历史</h3>
          <Button type="text" icon={<ClearOutlined />} onClick={clearChat} />
        </div>
        <ProList
          dataSource={chatHistory}
          renderItem={(item) => (
            <div className={styles.historyItem}>
              <Text ellipsis>{item.title}</Text>
              <Text type="secondary" className={styles.time}>{item.time}</Text>
            </div>
          )}
          metas={{
            title: {},
            description: {},
          }}
          split={true}
          size="small"
        />
      </div>

      {/* 右侧聊天区域 */}
      <div className={styles.chatMain}>
        {/* 聊天标题 */}
        <div className={styles.chatHeader}>
          <Space>
            <RobotOutlined style={{ fontSize: 20, color: '#FF6B35' }} />
            <span>AI 助手</span>
          </Space>
          <Button type="text" icon={<SettingOutlined />} />
        </div>

        {/* 消息列表 */}
        <div className={styles.messageList}>
          {messages.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="开始与 AI 助手对话"
            />
          ) : (
            <List
              dataSource={messages}
              renderItem={(item) => (
                <div className={`${styles.messageItem} ${styles[item.role]}`}>
                  <Avatar
                    icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    className={styles.avatar}
                    style={{
                      backgroundColor: item.role === 'user' ? '#FF6B35' : '#1890ff',
                    }}
                  />
                  <div className={styles.messageContent}>
                    <div className={styles.messageText}>{item.content}</div>
                    <div className={styles.messageTime}>
                      {item.timestamp.toLocaleTimeString()}
                    </div>
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

        {/* 输入区域 */}
        <div className={styles.inputArea}>
          <TextArea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入消息，按 Enter 发送，Shift + Enter 换行"
            autoSize={{ minRows: 1, maxRows: 4 }}
            className={styles.textarea}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            className={styles.sendButton}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  );
}
