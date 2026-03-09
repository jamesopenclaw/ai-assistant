export interface PIPipeline {
  id: string;
  name: string;
  repo: string;
  branch: string;
  status: 'success' | 'failed' | 'running' | 'pending' | 'cancelled';
  trigger: 'push' | 'pull_request' | 'manual' | 'schedule';
  lastRun: string;
  duration: string;
  author: string;
  commit: string;
}
