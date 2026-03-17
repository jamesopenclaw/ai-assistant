import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from '@umijs/max';
import {
  Avatar,
  Button,
  Card,
  Input,
  List,
  Space,
  Spin,
  Tag,
  Typography,
  Badge,
  Tooltip
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  WifiOutlined,
  DisconnectOutlined,
  ClearOutlined,
  SettingOutlined
} from '@ant-design/icons';
import styles from './index.less';

const { Text, Paragraph } = Typography;
const { TextArea } = Input;

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function RealtimeChatPage() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session') || 'realtime-' + Date.now();
  
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [connected, setConnected] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // 连接 WebSocket
  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/chat/${sessionId}`;
    
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setWs(websocket);
      wsRef.current = websocket;
    };
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'connected') {
          console.log('Connected:', data);
        } else if (data.type === 'message') {
          // AI 回复
          setThinking(false);
          const newMsg: MessageItem = {
            id: Date.now().toString(),
            role: 'assistant',
            content: data.content,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, newMsg]);
        } else if (data.type === 'status') {
          if (data.content === 'thinking') {
            setThinking(true);
          } else {
            setThinking(false);
          }
        } else if (data.type === 'error') {
          console.error('Error:', data.content);
          setThinking(false);
        }
      } catch (e) {
        console.error('Parse error:', e);
      }
    };
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      setWs(null);
      wsRef.current = null;
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
  };

  // 断开连接
  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setWs(null);
      setConnected(false);
    }
  };

  // 发送消息
  const sendMessage = () => {
    if (!inputValue.trim() || !connected) return;
    
    const content = inputValue.trim();
    setInputValue('');
    
    // 添加用户消息
    const userMsg: MessageItem = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    
    // 发送消息
    wsRef.current?.send(JSON.stringify({
      type: 'message',
      content
    }));
  };

  // 清除会话
  const clearSession = () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: 'clear' }));
    }
    setMessages([]);
  };

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 组件卸载时断开连接
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return (
    <div className={styles.realtimeChatContainer}>
      {/* 顶部状态栏 */}
      <div className={styles.header}>
        <Space>
          <Text strong>实时对话</Text>
          <Badge 
            status={connected ? "success" : "default"} 
            text={connected ? "已连接" : "未连接"} 
          />
          {connected ? (
            <Button 
              size="small" 
              danger 
              icon={<DisconnectOutlined />}
              onClick={disconnect}
            >
              断开
            </Button>
          ) : (
            <Button 
              size="small" 
              type="primary"
              icon={<WifiOutlined />}
              onClick={connect}
            >
              连接
            </Button>
          )}
        </Space>
        <Space>
          <Button 
            size="small" 
            icon={<ClearOutlined />}
            onClick={clearSession}
            disabled={!connected}
          >
            清除
          </Button>
        </Space>
      </div>

      {/* 消息列表 */}
      <div className={styles.messageList}>
        {!connected && messages.length === 0 && (
          <div className={styles.emptyState}>
            <RobotOutlined style={{ fontSize: 48, color: '#ccc' }} />
            <Text type="secondary">点击"连接"开始实时对话</Text>
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
              <Text type="secondary" className={styles.timestamp}>
                {msg.timestamp.toLocaleTimeString()}
              </Text>
            </div>
          </div>
        ))}
        
        {thinking && (
          <div className={styles.assistantMessage}>
            <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
            <div className={styles.messageContent}>
              <div className={styles.messageBubble}>
                <Space>
                  <Spin size="small" />
                  <Text type="secondary">AI 正在思考...</Text>
                </Space>
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
          placeholder={connected ? "输入消息，按 Enter 发送，Shift+Enter 换行" : "请先连接"}
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={!connected}
          style={{ flex: 1 }}
        />
        <Button 
          type="primary" 
          icon={<SendOutlined />}
          onClick={sendMessage}
          disabled={!connected || !inputValue.trim()}
        >
          发送
        </Button>
      </div>
    </div>
  );
}
