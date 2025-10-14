import type { ChatMessageVo } from '@/api/chat/types';
import { defineStore } from 'pinia';
import { getChatList } from '@/api/chat';
import { computed, ref } from 'vue';
import { useUserStore } from './user';

// 定义消息项类型
type MessageItem = {
  key: string | number;
  role: string;
  placement: 'start' | 'end';
  isMarkdown: boolean;
  avatar: string;
  avatarSize: string;
  typing: boolean;
  reasoning_content: string;
  thinkingStatus: string;
  content: string;
  thinkCollapse: boolean;
  workflow_events: any[];
  files?: any[];
} & Record<string, any>;

export const useChatStore = defineStore('chat', () => {
  const userStore = useUserStore();

  // 用户头像
  const avatar = computed(() => {
    const userInfo = userStore.userInfo;
    return userInfo?.avatar || 'https://avatars.githubusercontent.com/u/76239030?v=4';
  });

  // 是否开启深度思考
  const isDeepThinking = ref<boolean>(false);

  const setDeepThinking = (value: boolean) => {
    isDeepThinking.value = value;
  };

  // 会议ID对应-聊天记录 map对象
  const chatMap = ref<Record<string, MessageItem[]>>({});

  const setChatMap = (id: string, data: ChatMessageVo[]) => {
    // 数据验证
    if (!Array.isArray(data)) {
      chatMap.value[id] = [];
      return;
    }

    chatMap.value[id] = data.map((item: ChatMessageVo, index: number) => {
      // 确保消息对象存在且有必要的属性
      if (!item) {
        return {
          key: index,
          role: 'agent', // 改为 'agent' 而不是 'system'
          placement: 'start',
          isMarkdown: false,
          avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          avatarSize: '32px',
          typing: false,
          reasoning_content: '',
          thinkingStatus: 'end',
          content: '',
          thinkCollapse: false,
          workflow_events: [],
        } as MessageItem;
      }

      const isUser = item.role === 'user';
      // 确保 content 存在
      const content = item.content || '';
      // 从数据库字段 thought_content 获取思考内容
      const thoughtContent = (item as any).thought_content || '';

      // 从workflow_events中提取统计信息
      const workflowEvents = Array.isArray(item.workflow_events) ? item.workflow_events : [];// 检查是否有工作流完成事件
      // const finishedEvent = workflowEvents.find((event: any) => event.event === 'workflow_finished');
      
      // 从workflow_events中提取toolInfoList信息
      let toolInfoList: any[] = [];
      if (Array.isArray(workflowEvents)) {
        // 查找所有agent_thought事件并提取toolInfo
        workflowEvents.forEach((event: any) => {
          if (event.event === 'agent_thought' && event.toolInfo) {
            // 检查是否已存在相同的工具调用，避免重复
            const isDuplicate = toolInfoList.some((toolInfo: any) => 
              toolInfo.name === event.toolInfo.name && 
              JSON.stringify(toolInfo.input) === JSON.stringify(event.toolInfo.input)
            );
            
            if (!isDuplicate) {
              toolInfoList.push(event.toolInfo);
            }
          }
          // 也支持从data字段中提取toolInfo
          else if (event.data && event.data.toolInfo) {
            const isDuplicate = toolInfoList.some((toolInfo: any) => 
              toolInfo.name === event.data.toolInfo.name && 
              JSON.stringify(toolInfo.input) === JSON.stringify(event.data.toolInfo.input)
            );
            
            if (!isDuplicate) {
              toolInfoList.push(event.data.toolInfo);
            }
          }
        });
      }

      // 将API返回的workflow_events数据转换为前端期望格式
      const convertedWorkflowEvents = workflowEvents.map((event: any) => ({
        type: event.event || 'unknown',
        message: _getEventMessage(event),
        data: event,
        // 添加折叠状态，使事件数据默认折叠
        dataCollapsed: true,
      }));

      const processedItem = {
        ...item,
        key: item.id !== undefined ? item.id : index,
        role: isUser ? 'user' : 'agent', // 确保非用户消息的role是'agent'
        placement: isUser ? 'end' : 'start',
        isMarkdown: !isUser,
        avatar: isUser
          ? avatar.value
          : 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        avatarSize: '32px',
        typing: false,
        reasoning_content: thoughtContent, // 使用 thought_content 字段的值
        thought_content: thoughtContent, // 添加 thought_content 字段
        thinkingStatus: 'end',
        content: content, // 不再需要移除思考内容
        thinkCollapse: false,
        workflow_events: workflowEvents, // 保持原始数据用于向后兼容
        workflowEvents: convertedWorkflowEvents, // 使用转换后的数据
        // 添加工具调用信息列表
        toolInfoList: toolInfoList,
        // 添加工作流事件区域的折叠状态，默认折叠
        workflowEventsCollapsed: true,
        // 添加文件引用信息（如果存在）
        files: item.files || [],
        // 优先使用数据库中保存的total_tokens_estimated和cost字段
        totalTokens: item.total_tokens_estimated !== undefined && item.total_tokens_estimated !== null 
          ? item.total_tokens_estimated 
          : _extractTotalTokens(workflowEvents, item.totalTokens),
        totalCost: item.cost !== undefined && item.cost !== null 
          ? item.cost 
          : _extractTotalCost(workflowEvents, item.deductCost),
        // 添加时间戳信息
        timestamp: item.created_at ? formatTimestamp(item.created_at) : '',
      };

      // 根据规范，历史消息的AI思考过程内容应默认展开显示
      if (!isUser && (processedItem.thought_content || processedItem.reasoning_content)) {
        processedItem.thinkCollapse = false;
      }

      return processedItem as MessageItem;
    });
  };

  // 从workflow_events中提取总token数，优先使用statistics事件中的估算数据
  function _extractTotalTokens(workflowEvents: any[], fallbackValue: number = 0): number {
    // 首先检查是否有有效的回退值（来自数据库）
    if (fallbackValue !== undefined && fallbackValue !== null && fallbackValue > 0) {
      return fallbackValue;
    }
    
    // 其次查找statistics事件中的估算token数
    // 注意：我们需要检查两种可能的数据结构格式
    let statisticsEvent = workflowEvents.find((event: any) => event.event === 'statistics');

    // 如果没有找到，尝试另一种数据结构格式
    if (!statisticsEvent) {
      // 查找转换后的格式（在index.vue中使用的格式）
      statisticsEvent = workflowEvents.find((event: any) =>
        event.type === 'statistics' || (event.data && event.data.event === 'statistics'),
      )?.data;
    }

    if (statisticsEvent?.total_tokens_estimated) {
      return Number.parseInt(statisticsEvent.total_tokens_estimated) || 0;
    }
    if (statisticsEvent?.total_tokens) {
      return Number.parseInt(statisticsEvent.total_tokens) || 0;
    }

    // 再次查找workflow_finished事件中的token数
    let finishedEvent = workflowEvents.find((event: any) => event.event === 'workflow_finished');

    // 如果没有找到，尝试另一种数据结构格式
    if (!finishedEvent) {
      finishedEvent = workflowEvents.find((event: any) =>
        event.type === 'workflow_finished' || (event.data && event.data.event === 'workflow_finished'),
      )?.data;
    }

    if (finishedEvent?.total_tokens) {
      return Number.parseInt(finishedEvent.total_tokens) || 0;
    }

    // 最后使用后备值
    return fallbackValue;
  }

  // 从workflow_events中提取总费用，优先使用statistics事件中的估算费用
  function _extractTotalCost(workflowEvents: any[], fallbackValue: number = 0): number {
    // 首先检查是否有有效的回退值（来自数据库）
    if (fallbackValue !== undefined && fallbackValue !== null && fallbackValue > 0) {
      return fallbackValue;
    }
    
    // 其次查找statistics事件中的估算费用
    // 注意：我们需要检查两种可能的数据结构格式
    let statisticsEvent = workflowEvents.find((event: any) => event.event === 'statistics');

    // 如果没有找到，尝试另一种数据结构格式
    if (!statisticsEvent) {
      statisticsEvent = workflowEvents.find((event: any) =>
        event.type === 'statistics' || (event.data && event.data.event === 'statistics'),
      )?.data;
    }

    if (statisticsEvent?.estimated_cost) {
      return Number.parseFloat(statisticsEvent.estimated_cost) || 0;
    }
    if (statisticsEvent?.total_cost) {
      return Number.parseFloat(statisticsEvent.total_cost) || 0;
    }

    // 再次查找workflow_finished事件中的费用
    let finishedEvent = workflowEvents.find((event: any) => event.event === 'workflow_finished');

    // 如果没有找到，尝试另一种数据结构格式
    if (!finishedEvent) {
      finishedEvent = workflowEvents.find((event: any) =>
        event.type === 'workflow_finished' || (event.data && event.data.event === 'workflow_finished'),
      )?.data;
    }

    if (finishedEvent?.total_tokens) {
      // 按照每百万token 12元计算费用
      const tokens = Number.parseInt(finishedEvent.total_tokens) || 0;
      return (tokens / 1000000) * 12;
    }

    // 最后使用后备值
    return fallbackValue;
  }

  // 获取当前会话的聊天记录
  const requestChatList = async (sessionId: string) => {
    // 如果没有 token 则不查询聊天记录
    if (!userStore.token) {
      return;
    }
    try {
      const res = await getChatList({
        sessionId,
      });

      // 处理API响应对象，从res.data中获取实际数据
      let chatData: ChatMessageVo[] = [];
      // 直接检查res.data是否存在且为数组
      if (res && res.data && Array.isArray(res.data)) {
        chatData = res.data;
      }
      else if (res && Array.isArray(res)) {
        // 如果响应本身就是数组
        chatData = res;
      }
      else if (res && typeof res === 'object' && res !== null && !Array.isArray(res)) {
        // 处理其他可能的对象格式
        // 如果对象有 data 属性
        if ('data' in res && res.data) {
          if (Array.isArray(res.data)) {
            chatData = res.data;
          }
          else if (typeof res.data === 'object' && res.data !== null) {
            // 类型断言，确保res.data不是null也不是数组
            const dataObj = res.data as Record<string, any>;
            if ('rows' in dataObj && Array.isArray(dataObj.rows)) {
              chatData = dataObj.rows;
            }
          }
        }
        // 如果对象本身有类似数组的属性
        else if ('rows' in res && Array.isArray(res.rows)) {
          chatData = res.rows;
        }
      }

      // 直接使用获取到的数据，不需要额外的sessionId过滤
      setChatMap(sessionId, chatData);
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
    catch (error) {
    }
  };

  // 对思考中的内容回显做处理
  function extractThkContent(content: string) {
    // 匹配 var ... ``` 结构
    const regex = /var\s*([\s\S]*?)\s*\`\`\`/g;
    const matches = [];
    let match;
    
    // 提取所有匹配项
    while ((match = regex.exec(content)) !== null) {
      matches.push(match[1].trim());
    }
    
    // 返回所有思考内容，用换行符连接
    return matches.join('\n\n');
  }

  // 提取 think 标签后的内容
  function extractThkContentAfter(content: string) {
    // 保留 var ... ``` 结构中的内容
    const regex = /var\s*([\s\S]*?)\s*\`\`\`/g;
    return content.replace(regex, '$1');
  }

  // 移除 var 标签及其内容
  function removeThinkTag(content: string) {
    // 移除整个 var ... ``` 结构
    const regex = /var\s*[\s\S]*?\s*\`\`\`/g;
    return content.replace(regex, '').trim();
  }

  // 格式化时间戳
  function formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
    catch (error) {
      return timestamp; // 如果格式化失败，返回原始字符串
    }
  }

  // 辅助方法：根据事件类型生成事件消息
  function _getEventMessage(event: any): string {
    const eventType = event.event || 'unknown';

    switch (eventType) {
      case 'text_chunk':
        return `文本块: ${event.text || event.content || '无内容'}`;
      case 'workflow_started':
        return '工作流开始执行';
      case 'workflow_finished':
        return `工作流完成: ${event.status || '成功'}`;
      case 'node_started':
        return `节点开始: ${event.node_data?.title || event.node_data?.node_id || '未知节点'}`;
      case 'node_finished':
        return `节点完成: ${event.node_data?.title || event.node_data?.node_id || '未知节点'}`;
      case 'message':
        return `消息: ${event.answer || event.content || '无内容'}`;
      case 'message_end':
        return '消息结束';
      default:
        return `事件: ${eventType}`;
    }
  }

  return {
    avatar,
    isDeepThinking,
    setDeepThinking,
    chatMap,
    setChatMap,
    requestChatList,
    extractThkContent,
    extractThkContentAfter,
  };
});
