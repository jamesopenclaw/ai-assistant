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
      const token = localStorage.getItem('token');
      if (token) {
        config.headers = {
          ...(config.headers || {}),
          Authorization: `Bearer ${token}`,
        };
      }
      return config;
    },
  ],
  responseInterceptors: [
    async (response: any) => {
      if (response.status === 401) {
        localStorage.removeItem('token');
      }
      return response;
    },
  ],
};
