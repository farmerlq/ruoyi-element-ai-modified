import type { AgentVO } from '@/api/agent/types';
import { defineStore } from 'pinia';
import { getAgentList as getModelList } from '@/api/agent';
import { ref } from 'vue';

// 智能体管理
export const useModelStore = defineStore('model', () => {
  // 当前智能体
  const currentModelInfo = ref<AgentVO>({} as AgentVO);

  // 设置当前智能体
  const setCurrentModelInfo = (modelInfo: AgentVO) => {
    currentModelInfo.value = modelInfo;
  };

  // 智能体菜单列表
  const modelList = ref<AgentVO[]>([]);
  // 请求智能体菜单列表
  const requestModelList = async () => {
    try {
      const res = await getModelList();
      modelList.value = res.data;
    }
    catch (error) {
      // 处理请求模型列表错误
    }
  };

  return {
    currentModelInfo,
    setCurrentModelInfo,
    modelList,
    requestModelList,
  };
});