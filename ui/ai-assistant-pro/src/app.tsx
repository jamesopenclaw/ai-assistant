import { RuntimeConfig } from '@umijs/max';
import { requestConfig } from './request';

export const request: RuntimeConfig = {
  ...requestConfig,
};

export { requestConfig };
