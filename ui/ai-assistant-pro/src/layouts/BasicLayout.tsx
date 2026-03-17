import { ProLayout } from '@ant-design/pro-components';
import { Link } from '@umijs/max';
import React, { useState, useEffect } from 'react';
import { Select, Badge, Space } from 'antd';
import { accessIconMap } from '../access/access';

const loopMenuItem = (menus: any[]): any[] =>
  menus.map(({ icon, children, path, ...item }) => ({
    ...item,
    icon: icon && accessIconMap[icon as string],
    path,
    children: children && loopMenuItem(children),
  }));

// 获取租户列表
const fetchTenants = async () => {
  try {
    const res = await fetch('/api/tenants');
    return await res.json();
  } catch {
    return [{ id: 1, name: 'Default Tenant' }];
  }
};

// 获取用量统计
const fetchUsage = async (tenantId: number) => {
  try {
    const res = await fetch(`/api/usage?tenant_id=${tenantId}`, {
      headers: { 'X-Tenant-ID': String(tenantId) }
    });
    return await res.json();
  } catch {
    return { total_token_count: 0, total_request_count: 0 };
  }
};

export default function BasicLayout(props: { children: React.ReactNode }) {
  const { children } = props;
  const [tenants, setTenants] = useState<any[]>([]);
  const [currentTenant, setCurrentTenant] = useState<number>(1);
  const [usage, setUsage] = useState<any>({});

  useEffect(() => {
    // 加载租户列表
    fetchTenants().then(data => {
      setTenants(data);
      // 从 localStorage 获取上次选择的租户
      const saved = localStorage.getItem('currentTenantId');
      if (saved && data.find((t: any) => t.id === parseInt(saved))) {
        setCurrentTenant(parseInt(saved));
      }
    });
  }, []);

  useEffect(() => {
    // 加载用量统计
    fetchUsage(currentTenant).then(setUsage);
  }, [currentTenant]);

  const handleTenantChange = (value: number) => {
    setCurrentTenant(value);
    localStorage.setItem('currentTenantId', String(value));
  };

  // 默认菜单配置
  const defaultMenus = [
    {
      path: '/chat',
      name: 'AI 聊天',
      icon: 'MessageOutlined',
    },
    {
      path: '/sessions',
      name: '会话管理',
      icon: 'HistoryOutlined',
    },
    {
      path: '/autoreply',
      name: '关键词回复',
      icon: 'ApiOutlined',
    },
    {
      path: '/knowledge',
      name: '知识库',
      icon: 'BookOutlined',
    },
    {
      path: '/users',
      name: '用户管理',
      icon: 'TeamOutlined',
    },
    {
      path: '/templates',
      name: '对话模板',
      icon: 'AppstoreOutlined',
    },
    {
      path: '/cicd',
      name: 'CI/CD 流水线',
      icon: 'RocketOutlined',
    },
  ];

  return (
    <ProLayout
      title="小优 AI 助手"
      logo="https://img.icons8.com/color/96/artificial-intelligence.png"
      layout="side"
      fixedHeader
      fixSiderbar
      route={{
        path: '/',
        routes: loopMenuItem(defaultMenus),
      }}
      menu={{
        defaultOpenAll: true,
      }}
      menuExtraRender={() => (
        <div style={{ padding: '12px', textAlign: 'center' }}>
          <span style={{ color: '#FF6B35', fontWeight: 'bold' }}>AI Assistant Pro</span>
        </div>
      )}
      avatarProps={{
        src: 'https://img.icons8.com/color/96/user.png',
        size: 'small',
        title: '用户',
      }}
      actionsRender={() => [
        <span key="theme" style={{ cursor: 'pointer' }}>🌙</span>,
      ]}
      headerContentRender={() => (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px' }}>
          <div />
          <Space size="middle">
            {/* 用量统计显示 */}
            <Badge count={usage.total_request_count || 0} overflowCount={9999}>
              <span style={{ fontSize: '12px', color: '#666' }}>
                📊 {usage.total_token_count || 0} tokens
              </span>
            </Badge>
            {/* 租户切换 */}
            <Select
              value={currentTenant}
              onChange={handleTenantChange}
              style={{ width: 150 }}
              placeholder="选择租户"
            >
              {tenants.map(t => (
                <Select.Option key={t.id} value={t.id}>
                  {t.name}
                </Select.Option>
              ))}
            </Select>
          </Space>
        </div>
      )}
      onMenuHeaderClick={() => {
        window.location.href = '/';
      }}
      postMenuData={(menuData) => loopMenuItem(menuData || [])}
    >
      {children}
    </ProLayout>
  );
}
