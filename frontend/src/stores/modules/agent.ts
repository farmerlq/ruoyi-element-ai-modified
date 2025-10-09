import type { AgentVO } from '@/api/agent/types';
import { defineStore } from 'pinia';
import { getAgentList } from '@/api/agent';
import { ref } from 'vue'
// 智能体管理
export const useAgentStore = defineStore('agent', () => {
  // 当前智能体
  const currentAgentInfo = ref<AgentVO>({} as AgentVO);

  // 设置当前智能体
  const setCurrentAgentInfo = (agentInfo: AgentVO) => {
    currentAgentInfo.value = agentInfo;
  };

  // 智能体菜单列表
  const agentList = ref<AgentVO[]>([]);
  // 请求智能体菜单列表
  const requestAgentList = async () => {
    try {
      const res = await getAgentList();
      agentList.value = res.data;
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
    catch (error) {
    }
  };

  return {
    currentAgentInfo,
    setCurrentAgentInfo,
    agentList,
    requestAgentList,
  };
});
