<script setup lang="ts">
// 删除无法找到的模块导入，这些类型通常可以从组件本身获取或隐式推断
import { ArrowLeftBold, ArrowRightBold } from '@element-plus/icons-vue';
import { ElMessage, ElDrawer } from 'element-plus';
import { useHookFetch } from 'hook-fetch/vue';
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { Attachments, BubbleList, Sender, Thinking, XMarkdown } from 'vue-element-plus-x';
import { useRoute } from 'vue-router';
import { send } from '@/api';
import AgentSelect from '@/components/AgentSelect/index.vue';
import FilesSelect from '@/components/FilesSelect/index.vue';
import MessageActions from '@/components/MessageActions/index.vue';
import { useAgentStore } from '@/stores/modules/agent';
import { useChatStore } from '@/stores/modules/chat';
import { useFilesStore } from '@/stores/modules/files';
import { useSessionStore } from '@/stores/modules/session';
import { useUserStore } from '@/stores/modules/user';
import { DifyRenderer } from '@/utils/dify-parser';

/**
 * Thinking组件状态类型
 */
type ThinkingStatus = 'start' | 'end' | 'error' | 'thinking';

/**
 * 文件卡片属性接口 - 与vue-element-plus-x库兼容
 */
interface FilesCardProps {
  id?: string;
  name?: string;
  size?: number;
  url?: string;
  type?: string;
  status?: 'done' | 'error' | 'uploading' | string;
  [key: string]: any;
}

/**
 * Bubble列表项属性接口
 */
interface BubbleListItemProps {
  key?: number | string;
  role?: 'user' | 'agent' | string;
  avatar?: string;
  content?: string;
  placement?: 'start' | 'end';
  isMarkdown?: boolean;
  avatarSize?: string;
  typing?: boolean;
  loading?: boolean;
  thinkingStatus?: ThinkingStatus;
  thinkingCollapse?: boolean;
  reason_content?: string;
  reasoning_content?: string;
  workflowEvents?: WorkflowEventItem[];
  workflowEventsCollapsed?: boolean;
  workflow_events?: any[];
  thinkCollapse?: boolean;
  totalTokens?: number;
  totalCost?: number;
  timestamp?: string;
  noStyle?: boolean;
  files?: FilesCardProps[];
  [key: string]: any;
}

/**
 * Bubble列表实例接口
 */
interface BubbleListInstance {
  scrollToBottom: () => void;
  [key: string]: any;
}

/**
 * 工作流事件项接口
 */
interface WorkflowEventItem {
  event?: string;
  type?: string;
  message?: string;
  data: Record<string, any>;
  dataCollapsed?: boolean;
  id?: string; // 添加可选id字段
}

// 定义工作流事件类型

interface MessageItem extends BubbleListItemProps {
  key: number;
  role: 'user' | 'agent';
  avatar: string;
  content?: string;
  placement: 'start' | 'end';
  isMarkdown?: boolean;
  avatarSize?: string;
  typing?: boolean;
  loading?: boolean;
  thinkingStatus?: ThinkingStatus;
  thinkingCollapse?: boolean;
  reason_content?: string;
  reasoning_content?: string;
  workflowEvents?: WorkflowEventItem[];
  workflowEventsCollapsed?: boolean;
  workflow_events?: any[]; // 添加这个属性以匹配chatStore的类型要求
  thinkCollapse?: boolean;
  totalTokens?: number;
  totalCost?: number;
  timestamp?: string;
  noStyle?: boolean;
  files?: FilesCardProps[];
}

const route = useRoute();
const chatStore = useChatStore();
const agentStore = useAgentStore();
const filesStore = useFilesStore();
const userStore = useUserStore();
const sessionStore = useSessionStore();

// 消息操作抽屉
const messageActionsDrawer = ref(false);

// 用户头像
const avatar = computed(() => {
  const userInfo = userStore.userInfo;
  return userInfo?.avatar || new URL('@/assets/images/logo.png', import.meta.url).href;
});

const inputValue = ref('');
const senderRef = ref<InstanceType<typeof Sender> | null>(null);
const bubbleItems = ref<MessageItem[]>([]);
const bubbleListRef = ref<BubbleListInstance | null>(null);

// Dify响应渲染器
const difyRenderer = new DifyRenderer();

const { loading: isLoading, cancel } = useHookFetch({
  request: send,
  onError: () => {
    // 错误处理
  },
});
// 记录进入思考中
const isThinking = ref(false);

// 打开消息操作抽屉
const openMessageActions = () => {
  messageActionsDrawer.value = true;
};

// 处理保存消息
const handleSaveMessages = (messages: any[]) => {
  // 实际的保存逻辑
  console.log('保存消息:', messages);
  ElMessage.success(`已保存 ${messages.length} 条消息`);
  
  // 这里可以实现实际的保存逻辑，例如：
  // 1. 生成文件并下载
  // 2. 保存到数据库
  // 3. 发送到服务器
  
  // 示例：生成文本文件并下载
  const content = messages.map(msg => 
    `[${msg.role === 'user' ? '用户' : 'AI'}] ${msg.content}`
  ).join('\n\n');
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `聊天记录_${new Date().toISOString().slice(0, 10)}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 处理分享消息
const handleShareMessages = (messages: any[]) => {
  // 实际的分享逻辑
  console.log('分享消息:', messages);
  ElMessage.success(`已分享 ${messages.length} 条消息`);
  
  // 这里可以实现实际的分享逻辑，例如：
  // 1. 生成分享链接
  // 2. 复制到剪贴板
  // 3. 调用系统分享功能
  
  // 示例：将消息内容复制到剪贴板
  const content = messages.map(msg => 
    `[${msg.role === 'user' ? '用户' : 'AI'}] ${msg.content}`
  ).join('\n\n');
  
  navigator.clipboard.writeText(content)
    .then(() => {
      ElMessage.success('消息已复制到剪贴板');
    })
    .catch(() => {
      ElMessage.error('复制失败');
    });
};

// 监听打开消息操作的事件
const handleOpenMessageActions = () => {
  openMessageActions();
};

onMounted(() => {
  // 添加事件监听器
  window.addEventListener('open-message-actions', handleOpenMessageActions);
});

onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('open-message-actions', handleOpenMessageActions);
});

watch(
  () => route.params?.id,
  async (_id_) => {
    if (_id_) {
      // 确保_id_是一个有效的字符串
      const sessionId = typeof _id_ === 'object' ? String(_id_) : _id_;

      if (sessionId !== 'not_login') {
        // 判断的当前会话id是否有聊天记录，有缓存则直接赋值展示
        const chatData = chatStore.chatMap[sessionId];
        if (chatData && Array.isArray(chatData) && chatData.length > 0) {
          bubbleItems.value = chatData as MessageItem[];
          // 滚动到底部
          setTimeout(() => {
            bubbleListRef.value?.scrollToBottom();
          }, 350);
          return;
        }

        // 无缓存则请求聊天记录
        await chatStore.requestChatList(sessionId);
        // 请求聊天记录后，赋值回显，并滚动到底部
        const newChatData = chatStore.chatMap[sessionId];
        bubbleItems.value = (newChatData && Array.isArray(newChatData)) ? newChatData as MessageItem[] : [];

        // 滚动到底部
        setTimeout(() => {
          bubbleListRef.value?.scrollToBottom();
        }, 350);
      }

      // 如果本地有发送内容 ，则直接发送
      const v = localStorage.getItem('chatContent');
      if (v) {
        // 发送消息

        setTimeout(() => {
          startSSE(v);
        }, 350);

        localStorage.removeItem('chatContent');
      }
    }
  },
  { immediate: true, deep: true },
);

// 处理数据块 - 利用增强的DifyRenderer处理SSE数据
function handleDataChunk(chunk: any) {
  if (!chunk)
    return;

  try {
    const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
    if (!lastItem)
      return;

    // 使用增强的DifyRenderer处理数据块，支持多种格式
    difyRenderer.handleChunk(
      chunk,
      (content: string, _metadata?: Record<string, any>) => {
        if (content && content.trim().length > 0) {
          // 处理内容事件（text_chunk, message）- 直接使用流式内容，不使用打字机效果
          appendContent(content);
        }
      },
      (workflowEventData: Record<string, any>) => {
        // 处理工作流事件（workflow_started, node_started, node_finished, workflow_finished）
        const workflowEvent = workflowEventData;

        // 处理工作流事件数据

        // DifyRenderer传递了包含event、data和message字段的完整对象
        const eventType = workflowEvent.event || 'unknown';

        // 格式化事件消息
        const eventMessages: Record<string, string> = {
          workflow_started: '开始理解你的语义',
          node_started: '正在调用LLM（大模型）',
          node_finished: '调用完毕',
          workflow_finished: '任务完成',
          message_end: '消息已完成',
        };

        let message = eventMessages[eventType] || eventType;

        // 如果事件有自定义文本，使用自定义文本
        if (workflowEvent.message) {
          message = workflowEvent.message;
        }
        else if ((workflowEvent as any).text) {
          message = (workflowEvent as any).text;
        }

        // 为node_started事件添加更多信息
        if (eventType === 'node_started' && workflowEvent.data?.node_type) {
          message = `正在调用${workflowEvent.data.node_type}（${workflowEvent.data.node_name || workflowEvent.data.node_type}）`;
        }

        // 为node_finished事件添加更多信息
        if (eventType === 'node_finished' && workflowEvent.data?.node_name) {
          message = `${workflowEvent.data.node_name}调用完毕`;
        }

        // 确保lastItem.workflowEvents数组存在
        if (!lastItem.workflowEvents) {
          lastItem.workflowEvents = [];
        }

        // 创建新的workflowEvents数组以确保响应式更新
        const newWorkflowEvents = [...lastItem.workflowEvents];
        newWorkflowEvents.push({
          event: eventType,
          type: eventType,
          message,
          // 使用完整的workflowEvent对象，而不仅仅是data字段
          // 这样可以访问合并后的所有数据
          data: workflowEvent || {},
          dataCollapsed: true, // 默认折叠事件数据
          // 添加唯一ID以确保每个事件都是唯一的，有助于Vue的响应式系统识别变化
          id: Date.now() + Math.random().toString(36).substr(2, 9),
        });

        // 创建工作流事件项

        // 创建完全新的消息对象以确保响应式更新
        const updatedItem = {
          ...lastItem,
          workflowEvents: newWorkflowEvents,
          // 添加版本号属性，每次更新内容时递增，确保组件重新渲染
          eventsVersion: (lastItem.eventsVersion || 0) + 1,
        };

        // 如果是statistics事件，立即更新totalTokens和totalCost
        if (eventType === 'statistics' && workflowEvent.data) {
          if (workflowEvent.data.total_tokens_estimated) {
            updatedItem.totalTokens = Number.parseInt(workflowEvent.data.total_tokens_estimated) || updatedItem.totalTokens;
          }
          if (workflowEvent.data.estimated_cost) {
            updatedItem.totalCost = Number.parseFloat(workflowEvent.data.estimated_cost) || updatedItem.totalCost;
          }
        }
        // 如果是workflow_finished事件，也更新token信息
        else if (eventType === 'workflow_finished' && workflowEvent.data && workflowEvent.data.total_tokens) {
          updatedItem.totalTokens = Number.parseInt(workflowEvent.data.total_tokens) || updatedItem.totalTokens;
        }

        // 替换整个数组以确保响应式更新
        const newBubbleItems = [...bubbleItems.value];
        newBubbleItems[newBubbleItems.length - 1] = updatedItem;
        bubbleItems.value = newBubbleItems;

        // 使用nextTick确保DOM能够及时更新
        nextTick(() => {
          // 通知BubbleList组件更新
        });
      },
      () => {
        // 流式响应完成，由DifyRenderer内部调用

        finalizeMessage();
      },
      (error: Error) => {
        // 处理解析错误
        ElMessage.error(`消息解析出错：${error.message}`);
        finalizeMessage();
      },
    );
  }
  catch (error) {
    ElMessage.error('处理消息时出错，请稍后重试');
  }
}

// 追加内容到消息并触发BubbleList更新
function appendContent(content: string) {
  const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
  if (!lastItem || !content)
    return;

  const index = bubbleItems.value.length - 1;

  // 创建新对象确保响应式更新
  const updatedItem = {
    ...lastItem,
    content: (lastItem.content || '') + content,
    typing: false, // 保持typing为false，因为我们通过直接更新content来实现流式效果
    // 添加一个版本号属性，每次更新内容时递增，确保XMarkdown组件重新渲染
    renderVersion: (lastItem.renderVersion || 0) + 1,
  };

  // 替换整个数组以确保响应式系统检测到变化
  const newBubbleItems = [...bubbleItems.value];
  newBubbleItems[index] = updatedItem;
  bubbleItems.value = newBubbleItems;

  // 立即滚动到底部，确保用户实时看到内容
  bubbleListRef.value?.scrollToBottom();
}

// 完成消息处理 - 与BubbleList组件状态同步
function finalizeMessage() {
  const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
  if (!lastItem)
    return;

  // 创建更新后的消息对象
  const updatedItem = {
    ...lastItem,
    loading: false,
    typing: false, // 关闭打字机效果
  };

  // 从工作流事件中解析总token和总花费，优先使用估算值
  if (lastItem.workflowEvents && lastItem.workflowEvents.length > 0) {
    let totalTokens = 0;
    let totalCost = 0;

    // 优先查找statistics事件中的估算token数和费用
    const statisticsEvent = lastItem.workflowEvents.find((event: WorkflowEventItem) => event.type === 'statistics');
    if (statisticsEvent?.data) {
      if (statisticsEvent.data.total_tokens_estimated) {
        totalTokens = Number.parseInt(statisticsEvent.data.total_tokens_estimated) || 0;
      }
      else if (statisticsEvent.data.total_tokens) {
        totalTokens = Number.parseInt(statisticsEvent.data.total_tokens) || 0;
      }

      if (statisticsEvent.data.estimated_cost) {
        totalCost = Number.parseFloat(statisticsEvent.data.estimated_cost) || 0;
      }
      else if (statisticsEvent.data.total_cost) {
        totalCost = Number.parseFloat(statisticsEvent.data.total_cost) || 0;
      }
    }

    // 如果statistics事件没有提供足够信息，查找workflow_finished事件
    if (totalTokens === 0 || totalCost === 0) {
      const finishedEvent = lastItem.workflowEvents.find((event: WorkflowEventItem) => event.type === 'workflow_finished');
      if (finishedEvent?.data) {
        if (totalTokens === 0) {
          // 尝试从workflow_finished事件中获取各种可能的token值，但只取一个作为最终值
          if (finishedEvent.data.total_tokens) {
            totalTokens = Number.parseInt(finishedEvent.data.total_tokens) || 0;
          }
          else if (finishedEvent.data.usage?.total_tokens) {
            totalTokens = Number.parseInt(finishedEvent.data.usage.total_tokens) || 0;
          }
          else if (finishedEvent.data.execution_metadata?.total_tokens) {
            totalTokens = Number.parseInt(finishedEvent.data.execution_metadata.total_tokens) || 0;
          }
        }

        if (totalCost === 0) {
          // 尝试从workflow_finished事件中获取各种可能的费用值，但只取一个作为最终值
          if (finishedEvent.data.total_cost) {
            totalCost = Number.parseFloat(finishedEvent.data.total_cost) || 0;
          }
          else if (finishedEvent.data.cost) {
            totalCost = Number.parseFloat(finishedEvent.data.cost) || 0;
          }
          else if (finishedEvent.data.usage?.total_price) {
            totalCost = Number.parseFloat(finishedEvent.data.usage.total_price) || 0;
          }
          else if (finishedEvent.data.execution_metadata?.total_price) {
            totalCost = Number.parseFloat(finishedEvent.data.execution_metadata.total_price) || 0;
          }
        }
      }
    }

    // 更新项目的token和花费信息
    if (totalTokens > 0) {
      updatedItem.totalTokens = totalTokens;
    }
    if (totalCost > 0) {
      updatedItem.totalCost = totalCost;
    }
  }

  // 更新气泡项以触发渲染
  const index = bubbleItems.value.length - 1;
  bubbleItems.value[index] = updatedItem;
  isThinking.value = false;

  // 对话完成后自动折叠工作事件流
  if (lastItem.workflowEvents && lastItem.workflowEvents.length > 0) {
    // 使用nextTick确保DOM更新完成后再折叠
    nextTick(() => {
      const currentItems = bubbleItems.value;
      const currentIndex = currentItems.findIndex((i: MessageItem) => i.key === lastItem.key);
      if (currentIndex !== -1) {
        // 创建新数组和新对象确保响应式系统检测到变化
        const updatedItems = [...currentItems];
        updatedItems[currentIndex] = {
          ...updatedItems[currentIndex],
          workflowEventsCollapsed: true, // 自动折叠工作事件流
        };
        bubbleItems.value = updatedItems;

        // 工作事件流已自动折叠
      }
    });
  }

  // 最终滚动到底部，确保用户看到完整消息
  nextTick(() => {
    bubbleListRef.value?.scrollToBottom();
    // 添加延时检查，确保DOM更新后数据仍然存在
    setTimeout(() => {

    }, 100);
  });

  // 同步到存储，保持状态一致性
  syncToChatStore();
  // 消息发送完成后刷新会话列表，确保按更新时间排序
  refreshSessionList();
}

// 封装错误处理逻辑 - 确保错误信息也由AI回复显示
function handleError(err: any) {

  // 获取错误消息
  let errorMessage = '发送消息失败，请稍后重试';
  if (err?.message?.includes('会话不存在') || err?.msg?.includes('会话不存在')) {
    errorMessage = '当前会话不存在，请刷新页面或创建新会话';
    // 可以选择清空当前会话ID，让用户重新开始
    if (route.params?.id !== 'not_login') {
      // 可以在这里添加创建新会话的逻辑
    }
  }
  else if (err?.message) {
    errorMessage = err.message;
  }

  // 显示错误提示
  ElMessage.error(errorMessage);

  // 将错误信息作为AI的回复显示在聊天界面中
  const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
  if (lastItem && lastItem.role !== 'user') {
    // 更新最后一条AI消息为错误信息
    const index = bubbleItems.value.length - 1;
    bubbleItems.value[index] = {
      ...lastItem,
      content: `⚠️ ${errorMessage}`,
      loading: false,
      typing: false,
    };
  }
  else {
    // 如果没有最近的AI消息，则添加一条新的错误消息
    addMessage(`⚠️ ${errorMessage}`, false);
  }

  // 确保消息处于完成状态
  finalizeMessage();
}

async function startSSE(chatContent: string) {
  try {
    // 检查会话ID是否有效
    const currentSessionId = route.params?.id !== 'not_login' ? String(route.params?.id) : undefined;

    // 检查智能体ID是否有效 - agent_id是必需参数
    const agentId = agentStore.currentAgentInfo?.id; // 修复属性名：agentId -> id
    if (!agentId) {
      ElMessage.error('请先选择一个AI助手');
      return;
    }

    // 添加用户输入的消息
    inputValue.value = '';
    addMessage(chatContent, true);
    addMessage('', false);

    // 滚动到底部
    bubbleListRef.value?.scrollToBottom();

    // 构建消息列表，包含完整的对话历史
    const userMessages = bubbleItems.value
      ?.filter((item: any) => item?.content && (item?.role === 'user' || item?.role === 'system'))
      ?.map((item: any) => ({
        role: item.role === 'system' ? 'assistant' : item.role,
        content: item.content,
      })) || [];

    // 如果没有任何消息，不发送请求
    if (userMessages.length === 0) {
      ElMessage.warning('请输入消息内容');
      return;
    }

    // 构建后端期望的ChatRequest参数格式
    // 从userMessages中提取最后一个用户消息作为query
    const lastUserMessage = userMessages.findLast(msg => msg.role === 'user')?.content || userMessages[userMessages.length - 1]?.content || '';

    // 确保query字段不为空，否则使用当前输入的内容
    const finalQuery = lastUserMessage.trim() || chatContent.trim();

    // 添加文件引用到用户消息中（如果存在）
    let messageWithFiles = finalQuery;
    if (filesStore.filesList.length > 0) {
      messageWithFiles += "\n\n📁 已上传的文件:\n" + filesStore.filesList.map((file: FilesCardProps & { file: File }, index) => 
        `${index + 1}. ${file.name} (${file.uid})`
      ).join("\n") + "\n";
      
      // 清空文件列表
      filesStore.setFilesList([]);
    }

    if (!finalQuery) {
      ElMessage.warning('请输入消息内容');
      return;
    }

    const sendData = {
      query: messageWithFiles, // 使用包含文件引用的消息
      user_id: userStore.userInfo?.user_id, // 用户ID - 直接使用，后端会验证
      merchant_id: userStore.userInfo?.merchant_id, // 商户ID - 直接使用，后端会验证
      agent_id: agentId || 0, // 智能体ID - 修复：使用正确的agent_id而不是路由参数
      conversation_id: currentSessionId && currentSessionId !== 'not_login' ? String(currentSessionId) : undefined, // 会话ID
    };

    // 构建后端期望的参数

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api'}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`,
        },
        body: JSON.stringify(sendData),
      });

      if (!response.ok) {
        throw new Error('请求失败');
      }

      // 根据stream参数决定处理方式
      // 注意：后端现在根据智能体配置决定是否返回流式响应
      // 我们需要检查响应的Content-Type来决定如何处理
      const contentType = response.headers.get('Content-Type') || '';

      if (contentType.includes('text/event-stream')) {
        // 流式响应处理
        if (!response.body) {
          throw new Error('SSE连接失败');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // 重置DifyRenderer状态
        difyRenderer.reset();

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            // 通知DifyRenderer流已结束
            difyRenderer.notifyEnd();
            break;
          }

          // 立即处理每个数据块，避免buffer累积
          const chunkData = decoder.decode(value, { stream: true });

          // 将原始数据块传递给handleDataChunk，让DifyRenderer内部处理SSE格式
          handleDataChunk(chunkData);
        }
      }
      else {
        // 非流式响应处理
        const data = await response.json();

        // 处理非流式响应
        if (data.message) {
          // 更新最后一条消息的内容
          const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
          if (lastItem) {
            const updatedItem = {
              ...lastItem,
              content: data.message,
              loading: false,
              typing: false,
            };

            // 替换整个数组以确保响应式更新
            const newBubbleItems = [...bubbleItems.value];
            newBubbleItems[newBubbleItems.length - 1] = updatedItem;
            bubbleItems.value = newBubbleItems;
          }
        }

        // 处理工作流事件（如果有）
        if (data.workflow_events && Array.isArray(data.workflow_events)) {
          const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
          if (lastItem) {
            const updatedItem = {
              ...lastItem,
              workflowEvents: data.workflow_events.map((event: any) => ({
                type: event.event || 'unknown',
                message: event.answer || event.content || event.text || '',
                data: event,
                dataCollapsed: true,
              })),
            };

            // 替换整个数组以确保响应式更新
            const newBubbleItems = [...bubbleItems.value];
            newBubbleItems[newBubbleItems.length - 1] = updatedItem;
            bubbleItems.value = newBubbleItems;
          }
        }

        // 处理token统计信息（如果有）
        if (data.total_tokens_estimated !== undefined || data.estimated_cost !== undefined) {
          const lastItem = bubbleItems.value[bubbleItems.value.length - 1];
          if (lastItem) {
            const updatedItem = {
              ...lastItem,
              totalTokens: data.total_tokens_estimated || 0,
              totalCost: data.estimated_cost || 0,
            };

            // 替换整个数组以确保响应式更新
            const newBubbleItems = [...bubbleItems.value];
            newBubbleItems[newBubbleItems.length - 1] = updatedItem;
            bubbleItems.value = newBubbleItems;
          }
        }
      }
    }
    catch (error) {
      handleError(error);
    }
  }
  catch (err) {
    handleError(err);
  }
  finally {
    // 确保消息完成状态 - 使用统一的finalizeMessage处理
    finalizeMessage();
  }
}

// 中断请求
async function cancelSSE() {
  cancel();
  // 使用统一的完成处理
  finalizeMessage();
}

// 添加消息 - 维护聊天记录，确保与BubbleList组件兼容 - 改进组件引用访问
function addMessage(message: string, isUser: boolean) {
  // 确保bubbleItems.value是数组
  if (!Array.isArray(bubbleItems.value)) {
    bubbleItems.value = [];
  }

  const i = bubbleItems.value.length;
  const obj: MessageItem = {
    key: i,
    avatar: isUser
      ? avatar.value
      : new URL('@/assets/images/logo.png', import.meta.url).href,
    avatarSize: '32px',
    role: isUser ? 'user' : 'agent',
    placement: isUser ? 'end' : 'start',
    isMarkdown: !isUser,
    loading: false, // 移除Loading状态，避免阻塞数据流更新
    content: message || '',
    reasoning_content: '',
    thinkingStatus: 'start',
    thinkingCollapse: false, // 修复拼写错误: thinlCollapse -> thinkingCollapse
    // 初始化工作流事件数组
    workflowEvents: [],
    // 默认展开工作流事件
    workflowEventsCollapsed: false,
    // 移除打字机效果，直接显示流式内容
    typing: false,
    // 添加消息时间戳
    timestamp: new Date().toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }),
    // 如果是用户消息，添加当前的文件列表
    files: isUser ? [...filesStore.filesList] : [],
  };

  // 避免直接修改数组，使用新数组确保响应式更新
  const newBubbleItems = [...bubbleItems.value, obj];
  bubbleItems.value = newBubbleItems;

  // 确保BubbleList立即响应新消息
  nextTick(() => {
    if (bubbleListRef.value) {
      bubbleListRef.value.scrollToBottom();
    }
  });

  // 同步到chatStore
  syncToChatStore();
}

// 同步消息到chatStore
function syncToChatStore() {
  const currentSessionId = route.params?.id;
  if (currentSessionId && currentSessionId !== 'not_login') {
    chatStore.chatMap[String(currentSessionId)] = [...bubbleItems.value].map((item) => {
      // 从workflowEvents中提取估算token数，确保保存的是估算值而不是解析值
      let estimatedTokens = item.totalTokens || 0;
      let estimatedCost = item.totalCost || 0;

      // 如果有workflowEvents，优先使用其中的估算数据
      if (item.workflowEvents && Array.isArray(item.workflowEvents)) {
        // 查找statistics事件
        const statisticsEvent = item.workflowEvents.find((event: any) =>
          event.type === 'statistics' || (event.data && event.data.event === 'statistics'),
        )?.data;

        // 查找workflow_finished事件
        const finishedEvent = item.workflowEvents.find((event: any) =>
          event.type === 'workflow_finished' || (event.data && event.data.event === 'workflow_finished'),
        )?.data;

        // 优先使用statistics事件中的估算数据
        if (statisticsEvent) {
          if (statisticsEvent.total_tokens_estimated) {
            estimatedTokens = Number.parseInt(statisticsEvent.total_tokens_estimated) || estimatedTokens;
          }
          if (statisticsEvent.estimated_cost) {
            estimatedCost = Number.parseFloat(statisticsEvent.estimated_cost) || estimatedCost;
          }
        }
        // 其次使用workflow_finished事件中的数据
        else if (finishedEvent) {
          if (finishedEvent.total_tokens) {
            estimatedTokens = Number.parseInt(finishedEvent.total_tokens) || estimatedTokens;
          }
        }
      }

      return {
        key: item.key,
        role: item.role,
        placement: item.placement || (item.role === 'user' ? 'end' : 'start'),
        isMarkdown: item.isMarkdown !== undefined ? item.isMarkdown : (item.role !== 'user'),
        avatar: item.avatar,
        avatarSize: item.avatarSize || '32px',
        typing: item.typing || false,
        reasoning_content: item.reasoning_content || '',
        thinkingStatus: item.thinkingStatus || 'end',
        content: item.content || '',
        thinkCollapse: item.thinkCollapse || false,
        workflow_events: item.workflowEvents || [], // 正确映射属性名
        files: item.files || [],
        totalTokens: estimatedTokens,
        totalCost: estimatedCost,
        timestamp: item.timestamp || '',
      };
    });
  }
}

// 刷新会话列表，更新当前会话的更新时间
async function refreshSessionList() {
  const currentSessionId = route.params?.id;
  if (currentSessionId && currentSessionId !== 'not_login') {
    try {
      // 查找当前会话在会话列表中的信息
      const currentSession = sessionStore.sessionList.find(
        (session: any) => session.id === currentSessionId,
      );

      if (currentSession) {
        // 更新会话的updated_at时间为当前时间
        // 只传递后端API需要的字段，避免422错误
        const updatedSession = {
          id: currentSession.id,
          title: currentSession.title || '',
          user_id: currentSession.user_id,
          agent_id: currentSession.agent_id || 0,
          merchant_id: currentSession.merchant_id,
          status: currentSession.status || 'active',
        };

        // 调用会话存储的updateSession方法更新会话
        await sessionStore.updateSession(updatedSession);
      }
      else {
        // 如果当前会话不在列表中，刷新第一页数据
        await sessionStore.requestSessionList(1, true);
      }
    }
    catch (error) {
      // 刷新会话列表失败处理
    }
  }
}

// 展开收起 事件展示 - 添加实际实现以避免事件处理问题
function handleChange(value: { value: boolean; status: ThinkingStatus }) {
  // 实际处理逻辑，可以为空但不能只有注释
  // value参数需要被使用，以避免编译警告
  if (value) {
    // 可以在这里添加实际的展开/收起逻辑
  }
}

// 切换单个事件数据的展开/折叠状态 - 添加null检查并改进更新逻辑
function toggleEventData(item: MessageItem, eventIndex: number) {
  if (!item || !item.key) {
    return;
  }

  nextTick(() => {
    const index = bubbleItems.value.findIndex((i: MessageItem) => i.key === item.key);
    if (index !== -1 && bubbleItems.value[index] && bubbleItems.value[index].workflowEvents && bubbleItems.value[index].workflowEvents[eventIndex]) {
      // 创建新对象以确保响应式系统检测到变化
      const updatedItem = {
        ...bubbleItems.value[index],
        workflowEvents: [...bubbleItems.value[index].workflowEvents],
      };

      // 切换数据折叠状态
      updatedItem.workflowEvents[eventIndex] = {
        ...updatedItem.workflowEvents[eventIndex],
        dataCollapsed: !updatedItem.workflowEvents[eventIndex].dataCollapsed,
      };

      // 替换整个数组以确保响应式更新
      const newBubbleItems = [...bubbleItems.value];
      newBubbleItems[index] = updatedItem;
      bubbleItems.value = newBubbleItems;
    }
  });
}

// 切换整个工作流事件区域的展开/折叠状态
function toggleWorkflowEvents(item: MessageItem) {
  const currentItems = bubbleItems.value;
  const index = currentItems.findIndex((i: MessageItem) => i.key === item.key);
  if (index !== -1) {
    // 创建新数组和新对象确保响应式系统检测到变化
    const updatedItems = [...currentItems];
    updatedItems[index] = {
      ...updatedItems[index],
      workflowEventsCollapsed: !updatedItems[index].workflowEventsCollapsed,
    };
    bubbleItems.value = updatedItems;
  }
}

// BubbleList组件的更新钩子，确保数据更新时触发组件渲染
function handleBubbleListUpdate() {
  // 当数据更新时，可以执行额外的逻辑

  // 滚动到底部，确保用户看到最新内容
  bubbleListRef.value?.scrollToBottom();
}

function handleDeleteCard(_item: FilesCardProps, index: number) {
  filesStore.deleteFileByIndex(index);
}

watch(
  () => filesStore.filesList.length,
  (val) => {
    if (val > 0) {
      nextTick(() => {
        if (senderRef.value) {
          senderRef.value.openHeader();
        }
      });
    }
    else {
      nextTick(() => {
        if (senderRef.value) {
          senderRef.value.closeHeader();
        }
      });
    }
  },
);

</script>

<template>
  <div class="chat-with-id-container">
    <!-- 消息操作抽屉 -->
    <el-drawer
      v-model="messageActionsDrawer"
      title="消息操作"
      direction="rtl"
      size="50%"
    >
      <MessageActions 
        :messages="bubbleItems.map((item, index) => ({
          id: item.key || index,
          role: item.role as 'user' | 'agent',
          content: item.content || '',
          created_at: item.timestamp || new Date().toISOString()
        }))"
        @save="handleSaveMessages"
        @share="handleShareMessages"
      />
    </el-drawer>
    
    <div class="chat-warp">
      <!-- 使用自定义容器包装BubbleList，确保工作流事件能够正确布局 -->
      <div class="bubble-list-wrapper">
        <BubbleList
          ref="bubbleListRef" :list="bubbleItems as BubbleListItemProps[]" max-height="calc(100vh - 240px)"
          @update:list="handleBubbleListUpdate"
        >
          <template #header="{ item }">
            <Thinking
              v-if="(item as MessageItem).reasoning_content" v-model="(item as MessageItem).thinkingCollapse" :content="(item as MessageItem).reasoning_content"
              :status="(item as MessageItem).thinkingStatus as ThinkingStatus" class="thinking-chain-warp" @change="handleChange"
            />
          </template>

          <template #content="{ item }">
            <!-- chat 内容走 markdown -->
            <XMarkdown
              v-if="(item as MessageItem).content && (item as MessageItem).role === 'agent'" :key="(item as MessageItem).renderVersion" :markdown="(item as MessageItem).content || ''"
              class="chat-content" :themes="{ light: 'github-light', dark: 'github-dark' }"
              default-theme-mode="dark"
            />
            <!-- user 内容 纯文本 -->
            <div v-if="(item as MessageItem).content && (item as MessageItem).role === 'user'" class="user-content" v-html="(item as MessageItem).content?.replace(/\n/g, '<br>')">
            </div>

            <!-- 用户消息中的文件引用 -->
            <div v-if="(item as MessageItem).role === 'user' && (item as MessageItem).files && (item as MessageItem).files!.length > 0" class="user-files-reference">
              <div class="files-title">📁 引用的文件:</div>
              <div v-for="(file, index) in (item as MessageItem).files" :key="index" class="file-item">
                {{ index + 1 }}. {{ file.name || file.filename || file.title || '未知文件' }}
              </div>
            </div>

            <!-- 将工作流事件移动到content模板中，确保它们能够正确显示在消息下方 -->
            <!-- 工作流事件展示区域 -->
            <div v-if="(item as MessageItem).workflowEvents && (item as MessageItem).workflowEvents!.length > 0" class="workflow-events-container">
              <div class="workflow-events-toggle" @click="toggleWorkflowEvents(item as MessageItem)">
                <span class="workflow-events-label">
                  {{ (item as MessageItem).workflowEventsCollapsed ? '▼' : '▲' }} 工作流事件 ({{ (item as MessageItem).workflowEvents!.length }})
                </span>
              </div>

              <div v-if="!(item as MessageItem).workflowEventsCollapsed" class="workflow-events-content">
                <div v-for="(event, index) in (item as MessageItem).workflowEvents" :key="index" class="workflow-event-item">
                  <div class="event-header">
                    <span class="event-type">{{ event.type || event.event }}:</span>
                    <span class="event-message">{{ event.message }}</span>
                    <span
                      v-if="event.data && Object.keys(event.data).length > 0" class="event-data-toggle"
                      @click.stop="toggleEventData(item as MessageItem, index)"
                    >
                      {{ event.dataCollapsed ? '▼' : '▲' }}
                    </span>
                  </div>
                  <div v-if="event.data && Object.keys(event.data).length > 0 && !event.dataCollapsed" class="event-data">
                    {{ JSON.stringify(event.data, null, 2) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 显示token和花费统计信息 -->
            <div v-if="(((item as MessageItem).totalTokens || 0) > 0 || ((item as MessageItem).totalCost || 0) > 0) && (item as MessageItem).role === 'agent'" class="token-cost-info">
              <span v-if="(item as MessageItem).totalTokens" class="token-count">
                📊 Token: {{ (item as MessageItem).totalTokens }}
              </span>
              <span v-if="(item as MessageItem).totalCost" class="cost-amount">
                💰 花费: ¥{{ Number((item as MessageItem).totalCost).toFixed(4) }}
              </span>
              <span v-if="(item as MessageItem).timestamp" class="message-time">
                ⏰ 时间: {{ (item as MessageItem).timestamp }}
              </span>
            </div>
            <!-- 对于用户消息和没有统计数据的系统消息，单独显示时间 -->
            <div v-else-if="(item as MessageItem).timestamp" class="message-time-only">
              ⏰ 时间: {{ (item as MessageItem).timestamp }}
            </div>
          </template>
        </BubbleList>
      </div>

      <Sender
        ref="senderRef" v-model="inputValue" class="chat-defaul-sender" :auto-size="{
          maxRows: 6,
          minRows: 2,
        }" variant="updown" clearable allow-speech :loading="isLoading" @submit="startSSE" @cancel="cancelSSE"
      >
        <template #header>
          <div class="sender-header p-12px pt-6px pb-0px">
            <Attachments :items="filesStore.filesList as any" :hide-upload="true" @delete-card="handleDeleteCard">
              <template #prev-button="{ show, onScrollLeft }">
                <div
                  v-if="show"
                  class="prev-next-btn left-8px flex-center w-22px h-22px rounded-8px border-1px border-solid border-[rgba(0,0,0,0.08)] c-[rgba(0,0,0,.4)] hover:bg-#f3f4f6 bg-#fff font-size-10px"
                  @click="onScrollLeft"
                >
                  <el-icon>
                    <ArrowLeftBold />
                  </el-icon>
                </div>
              </template>

              <template #next-button="{ show, onScrollRight }">
                <div
                  v-if="show"
                  class="prev-next-btn right-8px flex-center w-22px h-22px rounded-8px border-1px border-solid border-[rgba(0,0,0,0.08)] c-[rgba(0,0,0,.4)] hover:bg-#f3f4f6 bg-#fff font-size-10px"
                  @click="onScrollRight"
                >
                  <el-icon>
                    <ArrowRightBold />
                  </el-icon>
                </div>
              </template>
            </Attachments>
          </div>
        </template>
        <template #prefix>
          <div class="flex items-center gap-8px flex-none">
            <FilesSelect />
            <AgentSelect />
          </div>
        </template>
      </Sender>
    </div>
  </div>
</template>

<style scoped lang="scss">
.chat-with-id-container {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;

  /* 聊天区域满宽 */
  .chat-warp {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
    height: calc(100vh - 60px);
    
    .thinking-chain-warp {
      margin-bottom: 12px;
    }
    
    // 新增包装器样式
    .bubble-list-wrapper {
      width: 80%;
      display: flex;
      flex-direction: column;
      max-width: none;
      margin-left: auto;
      margin-right: auto;
    }
    
    /* 文件引用样式 - 优化为列表样式 */
    .attachments {
      margin-bottom: 16px;
      width: 100%;
    }
    
    .attachments-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
    }
    
    .attachment-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px 20px;
      background: linear-gradient(135deg, #f8fafc, #f1f5f9);
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      transition: all 0.3s ease;
      cursor: pointer;
    }
    
    .attachment-item:hover {
      background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
      border-color: #cbd5e0;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .attachment-icon {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #4299e1;
      color: white;
      border-radius: 8px;
      flex-shrink: 0;
    }
    
    .attachment-info {
      flex: 1;
      min-width: 0;
    }
    
    .attachment-name {
      font-size: 15px;
      font-weight: 600;
      color: #2d3748;
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .attachment-details {
      display: flex;
      gap: 16px;
      font-size: 13px;
      color: #718096;
    }
    
    .attachment-size {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    
    .attachment-status {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    
    .attachment-actions {
      display: flex;
      gap: 8px;
      flex-shrink: 0;
    }
      

    
    .attachment-action-btn {
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      color: #718096;
      background-color: #edf2f7;
      transition: all 0.2s ease;
    }
    
    .attachment-action-btn:hover {
      background-color: #e2e8f0;
      color: #2d3748;
    }
  }
  
  .chat-defaul-sender {
    width: 80%;
    margin-bottom: 28px;
    padding: 0 24px;
    margin-left: 12px;
    margin-right: 12px;
  }
}

:deep() {
  .el-bubble-list {
    padding-top: 24px;
    width: 100%;
  }
  
  .el-bubble {
    padding: 0 12px;
    padding-bottom: 24px;
    width: 100%;
  }
  
  .el-typewriter {
    overflow: hidden;
    border-radius: 12px;
  }
  
  .user-content {
    // 换行
    white-space: pre-wrap;
  }
  
  /* 工作流事件样式优化 */
  .workflow-events-container {
    display: block;
    width: 100%;
    max-width: 100%;
    margin-top: 20px;
    overflow: hidden;
    background: #ffffff;
    border-radius: 8px;
    position: relative;
    border: 1px solid #e2e8f0;
  }
  
  // 工作流样式优化 - 简约设计
  .workflow-events-toggle {
    box-sizing: border-box;
    display: block;
    width: 100%;
    padding: 12px 16px;
    cursor: pointer;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 8px 8px 0 0;
    position: relative;
    overflow: hidden;
  }
  
  .workflow-events-toggle::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: #4299e1;
  }
  
  .workflow-events-label {
    display: flex;
    gap: 12px;
    align-items: center;
    font-size: 16px;
    font-weight: 600;
    color: #1a202c;
  }
  
  .workflow-events-content {
    box-sizing: border-box;
    display: block;
    width: 100%;
    max-height: 300px;
    padding: 0;
    overflow-y: auto;
    background-color: #ffffff;
    border-radius: 0 0 8px 8px;
    border: 1px solid #e2e8f0;
    border-top: none;
  }
  
  .workflow-event-item {
    box-sizing: border-box;
    display: block;
    width: 100%;
    padding: 16px 20px;
    border-bottom: 1px solid #f1f5f9;
    background-color: #ffffff;
    position: relative;
  }
  
  .workflow-event-item:last-child {
    border-bottom: none;
    border-radius: 0 0 8px 8px;
  }
  
  .event-header {
    box-sizing: border-box;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    width: 100%;
    margin-bottom: 8px;
  }
  
  .event-type {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    padding: 6px 12px;
    background: #4299e1;
    border-radius: 16px;
    flex-shrink: 0;
    display: inline-block;
  }
  
  .event-message {
    flex: 1;
    font-size: 14px;
    line-height: 1.5;
    color: #2d3748;
    padding: 0 12px;
    font-weight: 500;
  }
  
  .event-data-toggle {
    padding: 6px 12px;
    font-size: 14px;
    color: #ffffff;
    cursor: pointer;
    border-radius: 8px;
    background: #4a5568;
    border: none;
    flex-shrink: 0;
    font-weight: 500;
    display: inline-block;
  }
  
  .event-data {
    box-sizing: border-box;
    display: block;
    width: 100%;
    padding: 16px;
    margin-top: 12px;
    overflow-x: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: #1e293b;
    word-break: break-all;
    word-wrap: break-word;
    white-space: pre-wrap;
    background: #f8fafc;
    border: 1px solid #cbd5e0;
    border-radius: 8px;
  }

  // 滚动条样式优化
  .workflow-events-content::-webkit-scrollbar {
    width: 8px;
  }
  
  .workflow-events-content::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }
  
  .workflow-events-content::-webkit-scrollbar-thumb {
    background: #4299e1;
    border-radius: 4px;
  }
  
  .workflow-events-content::-webkit-scrollbar-thumb:hover {
    background: #3182ce;
  }
  
  .event-data::-webkit-scrollbar {
    height: 8px;
  }
  
  .event-data::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }
  
  .event-data::-webkit-scrollbar-thumb {
    background: #4299e1;
    border-radius: 4px;
  }
  
  .event-data::-webkit-scrollbar-thumb:hover {
    background: #3182ce;
  }

  /* 统计数据样式优化 - 简约设计 */
  .token-cost-info {
    display: flex;
    flex-wrap: nowrap;
    gap: 20px;
    padding: 12px 16px;
    margin-top: 16px;
    font-size: 14px;
    color: #4a5568;
    background: #f8fafc;
    border: 1px solid #c6f6d5;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
  }
  
  .token-cost-info::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: #4299e1;
  }
  
  .token-count,
  .cost-amount,
  .message-time {
    display: flex;
    gap: 8px;
    align-items: center;
    font-weight: 500;
  }
  
  .token-count .value,
  .cost-amount .value,
  .message-time .value {
    color: #0f172a;
    font-weight: 600;
  }
  
  .message-time-only {
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 14px;
    color: #718096;
    text-align: right;
    font-style: italic;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
  
  /* 用户消息中的文件引用样式 */
  .user-files-reference {
    margin-top: 12px;
    padding: 12px;
    background-color: #f1f5f9;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    font-size: 14px;
  }
  
  .user-files-reference .files-title {
    font-weight: 600;
    margin-bottom: 8px;
    color: #4a5568;
  }
  
  .user-files-reference .file-item {
    padding: 4px 0;
    color: #4a5568;
    font-size: 14px;
    line-height: 1.4;
  }
}
</style>