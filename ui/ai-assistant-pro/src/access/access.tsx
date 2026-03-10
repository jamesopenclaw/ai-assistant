import React from 'react';
import * as Icons from '@ant-design/icons';

// 图标映射，用于动态渲染菜单图标
export const accessIconMap: Record<string, React.ReactNode> = {
  MessageOutlined: <Icons.MessageOutlined />,
  RocketOutlined: <Icons.RocketOutlined />,
  BookOutlined: <Icons.BookOutlined />,
  AppstoreOutlined: <Icons.AppstoreOutlined />,
  UserOutlined: <Icons.UserOutlined />,
  SettingOutlined: <Icons.SettingOutlined />,
  DashboardOutlined: <Icons.DashboardOutlined />,
  FileTextOutlined: <Icons.FileTextOutlined />,
  CloudServerOutlined: <Icons.CloudServerOutlined />,
};

// 权限定义
export type AccessType = 'canAdmin' | 'canUser' | 'canGuest';

// 初始权限（模拟从后端获取）
const initialAccess: AccessType[] = ['canAdmin', 'canUser'];

/**
 * 权限判断函数
 * @param {any} initialState - 初始状态，包含用户信息
 * @param {any} permission - 权限对象
 * @returns {boolean} - 是否有权限
 */
export default function access(
  initialState: { currentUser?: { role?: string } } | undefined,
  permission: { name?: string }
): boolean {
  // 如果没有用户信息，只有 guest 权限
  if (!initialState?.currentUser) {
    return permission.name === 'canGuest';
  }

  const { role } = initialState.currentUser || {};

  // 根据用户角色判断权限
  switch (permission.name) {
    case 'canAdmin':
      return role === 'admin';
    case 'canUser':
      return role === 'user' || role === 'admin';
    case 'canGuest':
      return true;
    default:
      return false;
  }
}

/**
 * 获取初始权限
 */
export function getInitialAccess(): AccessType[] {
  return initialAccess;
}
