// 智能体列表返回的数据结构
export interface AgentVO {
  id: number;
  merchant_id: number;
  name: string;
  description: string;
  type: string;
  config: Record<string, any>;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}
