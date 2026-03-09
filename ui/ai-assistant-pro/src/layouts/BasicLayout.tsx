import { ProLayout } from '@ant-design/pro-components';
import { Link } from '@umijs/max';
import { Result } from 'antd';
import React from 'react';
import { accessIconMap } from '../access/access';

const loopMenuItem = (menus: any[]): any[] =>
  menus.map(({ icon, children, path, ...item }) => ({
    ...item,
    icon: icon && accessIconMap[icon as string],
    path,
    children: children && loopMenuItem(children),
  }));

export default function BasicLayout(props: { children: React.ReactNode }) {
  const { children } = props;

  // 默认菜单配置
  const defaultMenus = [
    {
      path: '/chat',
      name: 'AI 聊天',
      icon: 'MessageOutlined',
    },
    {
      path: '/cicd',
      name: 'CI/CD 流水线',
      icon: 'RocketOutlined',
    },
    {
      path: '/knowledge',
      name: '知识库',
      icon: 'BookOutlined',
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
      onMenuHeaderClick={() => {
        window.location.href = '/';
      }}
      postMenuData={(menuData) => loopMenuItem(menuData || [])}
    >
      {children}
    </ProLayout>
  );
}
