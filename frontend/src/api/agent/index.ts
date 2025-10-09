import type { AgentVO } from './types';
import { get } from '@/utils/request';

// 获取当前用户的智能体列表
export function getAgentList() {
  return get<AgentVO[]>('/agents/');
}
