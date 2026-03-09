import { defineConfig } from '@umijs/max';

export default defineConfig({
  routes: [
    {
      path: '/user',
      routes: [
        {
          path: '/user/login',
          name: '登录',
          component: './user/login',
        },
        {
          path: '/user/register',
          name: '注册',
          component: './user/register',
        },
      ],
    },
    {
      path: '/',
      component: '../layouts/BasicLayout',
      routes: [
        {
          path: '/',
          redirect: '/chat',
        },
        {
          path: '/chat',
          name: 'AI 聊天',
          icon: 'MessageOutlined',
          component: './chat',
        },
        {
          path: '/cicd',
          name: 'CI/CD 流水线',
          icon: 'RocketOutlined',
          component: './cicd',
        },
        {
          path: '/knowledge',
          name: '知识库',
          icon: 'BookOutlined',
          component: './knowledge',
        },
      ],
    },
  ],
  npmClient: 'npm',
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
});
