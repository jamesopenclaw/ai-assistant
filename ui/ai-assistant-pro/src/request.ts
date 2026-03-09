import { RequestConfig } from '@umijs/max';

export const requestConfig: RequestConfig = {
  timeout: 10000,
  errorConfig: {
    errorHandler: (error: any) => {
      console.error('Request error:', error);
    },
  },
  requestInterceptors: [
    (config: any) => {
      // 拦截请求配置
      const token = localStorage.getItem('token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
  ],
  responseInterceptors: [
    (response: any) => {
      // 拦截响应
      const { data } = response;
      if (data.code !== 200) {
        console.error('Response error:', data.message);
      }
      return response;
    },
  ],
};
