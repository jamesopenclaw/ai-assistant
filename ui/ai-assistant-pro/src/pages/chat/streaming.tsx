import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from '@umijs/max';
import {
  Avatar,
  Button,
  Input,
  Space,
  Spin,
  Typography,
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import styles from './index.less';

const { Text } = Typography;
const { TextArea } = Input;

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  streaming?: boolean;
}

export default function StreamingChatPage() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session') || 'stream-' + Date.now();
  
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [currentReply, setCurrentReply] = useState('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentReply]);

  // 发送消息
  const sendMessage = async () => {
    if (!inputValue.trim() || streaming) return;
    
    const userMessage: MessageItem = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setStreaming(true);
    setCurrentReply('');
    
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': localStorage.getItem('currentTenantId') || '1'
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId
        })
      });
      
      if (!response.ok) throw new Error('请求失败');
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error('No reader');
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                setCurrentReply(prev => prev + '\n[错误: ' + data.error + ']');
              } else if (data.done) {
                // 完成
                const assistantMessage: MessageItem = {
                  id: (Date.now() + 1).toString(),
                  role: 'assistant',
                  content: currentReply,
                  timestamp: new Date()
                };
                setMessages(prev => [...prev, assistantMessage]);
                setCurrentReply('');
                setStreaming(false);
              } else if (data.content) {
                setCurrentReply(prev => prev + data.content);
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error);
      setCurrentReply(prev => prev + '\n[请求失败]');
      setStreaming(false);
    }
  };

  // 打字动画效果
  const renderContent = (content: string, isStreaming: boolean = false) => {
    if (isStreaming && content) {
      return (
        <span>
          {content}
          <span className={styles.cursor}>▊</span>
        </span>
      );
    }
    return content;
  };

  return (
    <div className={styles.chatContainer}>
      {/* 消息列表 */}
      <div className={styles.messageList}>
        {messages.length === 0 && !streaming && (
          <div className={styles.emptyState}>
            <ThunderboltOutlined style={{ fontSize: 48, color: '#FF6B35' }} />
            <Text type="secondary">开始对话，体验流式输出</Text>
          </div>
        )}
        
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={msg.role === 'user' ? styles.userMessage : styles.assistantMessage}
          >
            <Avatar 
              icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
              style={{ 
                backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a'
              }}
            />
            <div className={styles.messageContent}>
              <div className={styles.messageBubble}>
                {msg.content}
              </div>
            </div>
          </div>
        ))}
        
        {/* 正在流式输出 */}
        {streaming && (
          <div className={styles.assistantMessage}>
            <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
            <div className={styles.messageContent}>
              <div className={styles.messageBubble}>
                {renderContent(currentReply, true)}
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className={styles.inputArea}>
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="输入消息，按 Enter 发送"
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={streaming}
          style={{ flex: 1 }}
        />
        <Button 
          type="primary" 
          icon={<SendOutlined />}
          onClick={sendMessage}
          disabled={!inputValue.trim() || streaming}
          loading={streaming}
        >
          {streaming ? '发送中' : '发送'}
        </Button>
      </div>
    </div>
  );
}
