<template>
  <div v-if="showThinkingContent" class="thinking-process-container">
    <div class="events-header" @click="toggleThinkingProcess">
      <el-icon class="events-icon">
        <Collection />
      </el-icon>
      <span class="events-title">AI 思考过程</span>
      <el-tag type="info" size="small" class="events-tag">点击展开/收起</el-tag>
      <el-icon class="collapse-icon" :class="{ 'is-collapsed': thinkingProcessCollapsed }">
        <ArrowDown />
      </el-icon>
    </div>

    <transition name="slideFade">
      <div v-show="!thinkingProcessCollapsed" class="events-list">
        <div class="event-item event-thinking">
          <div class="event-header" @click="toggleThinkingDetail">
            <el-icon class="event-icon">
              <InfoFilled />
            </el-icon>
            <span class="event-type">思考过程</span>
            <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': thinkingDetailCollapsed }">
              <ArrowDown />
            </el-icon>
          </div>
          <div v-if="displayThinkingContent" class="event-message" :class="{ 'is-collapsed': thinkingDetailCollapsed }">
            {{ displayThinkingContent }}
          </div>
        </div>

        <!-- 工具调用信息 -->
        <div v-for="(toolCall, index) in validToolCalls" :key="`${index}-${toolCall.name || 'unnamed'}-${Date.now()}`"
          class="event-item event-tool-call">
          <div class="event-header" @click="toggleToolCallDetail(index)">
            <el-icon class="event-icon">
              <component :is="getToolCallIcon(toolCall)" />
            </el-icon>
            <span class="event-type">使用工具 {{ getToolCallType(toolCall) }}</span>
            <!-- 调试信息 -->
            <span v-if="!toolCall.name || toolCall.name.trim() === ''" class="debug-info">[未命名工具]</span>
            <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': toolCallCollapsed[index] }">
              <ArrowDown />
            </el-icon>
          </div>
          <div class="event-raw-data" :class="{ 'is-collapsed': toolCallCollapsed[index] }">
            <div class="tool-section">
              <div class="tool-section-title">请求:</div>
              <pre>{{ formatToolCallData(toolCall.input || toolCall.tool_input) }}</pre>
            </div>
            <div class="tool-section">
              <div class="tool-section-title">响应:</div>
              <pre>{{ formatToolCallData(toolCall.observation) }}</pre>
            </div>
            <!-- 原始数据调试 -->
            <!-- 开发环境调试信息 -->
            <!-- <div v-if="__DEV__" class="debug-section">
              <div class="debug-title">原始数据:</div>
              <pre>{{ JSON.stringify(toolCall, null, 2) }}</pre>
            </div> -->
          </div>
        </div>

        <!-- 其他事件信息 -->
        <div v-if="props.otherEvents && Array.isArray(props.otherEvents) && props.otherEvents.length > 0"
          class="event-item event-other-events">
          <div class="event-header" @click="toggleOtherEvents">
            <el-icon class="event-icon">
              <InfoFilled />
            </el-icon>
            <span class="event-type">其他事件</span>
            <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': otherEventsCollapsed }">
              <ArrowDown />
            </el-icon>
          </div>
          <div class="event-message" :class="{ 'is-collapsed': otherEventsCollapsed }">
            <div v-for="(event, index) in props.otherEvents" :key="index" class="other-event-item">
              <div class="other-event-title">事件 #{{ index + 1 }}:</div>
              <pre>{{ formatOtherEventData(event) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  Collection,
  ArrowDown,
  InfoFilled,
  Tools
} from '@element-plus/icons-vue'

const props = defineProps<{
  thinkingContent?: string | Record<string, any> | Array<any>
  reasoningEvents?: Array<any>
  otherEvents?: Array<any>
  toolInfoList?: Array<{
    name?: string
    tool?: string
    toll?: string  // 添加对toll字段的支持
    input?: string
    tool_input?: string
    observation?: string
  }>
  // 添加toolInfoVersion属性用于触发更新
  toolInfoVersion?: number
}>()

// AI思考过程相关状态
const thinkingProcessCollapsed = ref(false)
const thinkingDetailCollapsed = ref(false)
// 工具调用数组
const toolCalls = ref<any[]>([])
// AI思考内容，可能来自thinkingContent或reasoningEvents
const displayThinkingContent = computed(() => {
  // 优先使用reasoningEvents
  if (props.reasoningEvents && Array.isArray(props.reasoningEvents) && props.reasoningEvents.length > 0) {
    // 如果是数组，将其转换为字符串
    if (Array.isArray(props.reasoningEvents)) {
      return props.reasoningEvents.map(event => {
        if (typeof event === 'object' && event !== null) {
          // 如果对象有特定字段，显示它们
          if (event.thought) return event.thought;
          if (event.content) return event.content;
          if (event.observation) return event.observation;
          // 否则转换为JSON字符串
          return JSON.stringify(event, null, 2);
        }
        // 否则直接返回
        return String(event);
      }).join('\n');
    }
    return props.reasoningEvents;
  }
  // 其次使用thinkingContent
  if (props.thinkingContent) {
    if (typeof props.thinkingContent === 'object') {
      return JSON.stringify(props.thinkingContent, null, 2);
    }
    return String(props.thinkingContent);
  }
  return '';
})
// 判断是否应该显示思考内容区域
const showThinkingContent = computed(() => {
  // 简化显示逻辑，只要有工具调用就显示
  const hasToolCalls = toolCalls.value && toolCalls.value.length > 0;
  
  console.log('Show thinking content check:', {
    hasToolCalls,
    toolCalls: toolCalls.value,
    reasoningEvents: props.reasoningEvents,
    thinkingContent: props.thinkingContent,
    otherEvents: props.otherEvents
  });

  return (
    (props.reasoningEvents && Array.isArray(props.reasoningEvents) && props.reasoningEvents.length > 0) ||
    (props.thinkingContent &&
      ((typeof props.thinkingContent === 'string' && props.thinkingContent.trim() !== '') ||
        (typeof props.thinkingContent === 'object' && props.thinkingContent !== null))) ||
    hasToolCalls ||
    (props.otherEvents && Array.isArray(props.otherEvents) && props.otherEvents.length > 0)
  )
})

// 工具调用折叠状态数组，默认为true（折叠）
const toolCallCollapsed = ref<Array<boolean>>([])
// 其他事件折叠状态
const otherEventsCollapsed = ref(true)

// 初始化时确保所有现有的工具调用都是折叠状态
const initializeToolCallCollapsed = () => {
  if (toolCalls.value.length > 0) {
    // 确保toolCallCollapsed数组长度与toolCalls一致
    while (toolCallCollapsed.value.length < toolCalls.value.length) {
      // 根据规范，历史消息的AI思考过程内容应默认展开显示
      // 但对于工具调用，我们仍然默认折叠，因为它们可能很长
      toolCallCollapsed.value.push(true); // 默认折叠
    }
    // 对于超出的部分，保持原状态
    if (toolCallCollapsed.value.length > toolCalls.value.length) {
      toolCallCollapsed.value.splice(toolCalls.value.length);
    }
  } else {
    // 如果没有工具调用，清空折叠状态数组
    toolCallCollapsed.value = [];
  }
};

// 立即执行一次初始化
initializeToolCallCollapsed();

// 安全地解析JSON字符串，处理各种边缘情况
const safelyParseJSON = (data: any): any => {
  if (data === null || data === undefined) {
    return 'null';
  }

  if (typeof data === 'object') {
    return data;
  }

  if (typeof data === 'string') {
    // 检查字符串是否看起来像JSON
    if ((data.startsWith('{') && data.endsWith('}')) ||
      (data.startsWith('[') && data.endsWith(']'))) {
      try {
        return JSON.parse(data);
      } catch (e) {
        // 解析失败时，返回原始字符串并添加提示
        return `[可能不是有效JSON] ${data}`;
      }
    }

    // 如果是包含JSON的字符串，但有额外内容，尝试提取JSON部分
    try {
      // 尝试找到第一个{和最后一个}，提取JSON部分
      const firstBrace = data.indexOf('{');
      const lastBrace = data.lastIndexOf('}');
      if (firstBrace !== -1 && lastBrace !== -1 && firstBrace < lastBrace) {
        const potentialJson = data.substring(firstBrace, lastBrace + 1);
        return JSON.parse(potentialJson);
      }
    } catch (e) {
      // 如果尝试提取失败，继续使用原始数据
    }
  }

  // 其他情况直接返回
  return data;
};

// 从thinkingContent文本中提取工具调用信息，包括观察结果
const extractToolCallsFromText = (text: string): any[] => {
  const toolCalls: any[] = [];
  if (!text) return toolCalls;

  // 不再从full_thought_content提取工具调用信息，直接返回空数组
  return toolCalls;
};

// 比较两个工具调用是否相同，包括观察结果
const areToolCallsEqual = (call1: any, call2: any): boolean => {
  if (!call1 || !call2) return false;

  // 比较核心属性
  if (call1.name !== call2.name) return false;

  // 深度比较input对象
  try {
    const inputEqual = JSON.stringify(call1.input) === JSON.stringify(call2.input);
    const observationEqual = JSON.stringify(call1.observation) === JSON.stringify(call2.observation);
    return inputEqual && observationEqual;
  } catch {
    // 如果JSON序列化失败，进行简单比较
    return String(call1.input) === String(call2.input) && String(call1.observation) === String(call2.observation);
  }
};

// 标记是否已经从toolInfoList获取了工具调用信息
const hasToolInfoList = ref(false);

// 去重工具调用数组
const deduplicateToolCalls = (calls: any[]): any[] => {
  const uniqueCalls: any[] = [];

  calls.forEach(call => {
    // 检查这个调用是否已经在uniqueCalls中
    const isDuplicate = uniqueCalls.some(uniqueCall =>
      areToolCallsEqual(call, uniqueCall)
    );

    // 如果不是重复的，则添加到uniqueCalls
    if (!isDuplicate) {
      uniqueCalls.push(call);
    }
  });

  return uniqueCalls;
};

// 工具调用过滤函数
const isValidToolCall = (toolCall: any): boolean => {
  // 检查工具调用是否有效
  if (!toolCall) return false;

  // 检查工具名称是否存在且不为空
  if (!toolCall.name || toolCall.name === '未命名工具' || toolCall.name.trim() === '') {
    return false;
  }

  // 检查是否至少有输入或观察结果之一
  const hasInput = toolCall.input && (
    (typeof toolCall.input === 'string' && toolCall.input.trim() !== '') ||
    (typeof toolCall.input === 'object' && Object.keys(toolCall.input).length > 0)
  );

  const hasObservation = toolCall.observation && (
    (typeof toolCall.observation === 'string' && toolCall.observation.trim() !== '') ||
    (typeof toolCall.observation === 'object' && Object.keys(toolCall.observation).length > 0)
  );

  // 实时消息中必须有过输入或观察结果
  if (!hasInput && !hasObservation) {
    return false;
  }

  // 检查观察结果是否为"等待响应"相关文本
  if (typeof toolCall.observation === 'string') {
    // 定义等待响应相关的关键词
    const waitingKeywords = ['等待响应', 'loading', 'pending', '等待中'];
    const isWaitingResponse = waitingKeywords.some(keyword =>
      toolCall.observation.toLowerCase().includes(keyword.toLowerCase()));

    // 如果是等待响应状态，则过滤掉（在历史消息中不显示）
    if (isWaitingResponse) {
      return false;
    }
  }

  // 允许没有观察结果的工具调用（可能是在保存时还没有收到响应）
  return true;
};

// 更严格的工具调用有效性检查，专门用于历史消息
const isHistoricalValidToolCall = (toolCall: any): boolean => {
  // 检查工具调用是否有效
  if (!toolCall) return false;

  // 检查工具名称是否存在且不为空
  if (!toolCall.name || toolCall.name === '未命名工具' || toolCall.name.trim() === '') {
    return false;
  }

  // 检查是否至少有输入或观察结果之一
  const hasInput = (toolCall.input !== undefined && toolCall.input !== null) && (
    (typeof toolCall.input === 'string' && toolCall.input.trim() !== '') ||
    (typeof toolCall.input === 'object' && Object.keys(toolCall.input).length > 0)
  );

  const hasObservation = (toolCall.observation !== undefined && toolCall.observation !== null) && (
    (typeof toolCall.observation === 'string' && toolCall.observation.trim() !== '') ||
    (typeof toolCall.observation === 'object' && Object.keys(toolCall.observation).length > 0)
  );

  // 历史消息中至少需要有输入或观察结果之一
  if (!hasInput && !hasObservation) {
    // 对于历史消息，即使没有输入和观察结果，只要工具名称存在也可以显示
    // 因为这可能是数据库中存储的完整信息
    return true;
  }

  // 检查观察结果是否为"等待响应"相关文本
  if (toolCall.observation && typeof toolCall.observation === 'string') {
    // 定义等待响应相关的关键词
    const waitingKeywords = ['等待响应', 'loading', 'pending', '等待中'];
    const isWaitingResponse = waitingKeywords.some(keyword =>
      toolCall.observation.toLowerCase().includes(keyword.toLowerCase()));

    // 如果是等待响应状态，则过滤掉（在历史消息中不显示）
    if (isWaitingResponse) {
      return false;
    }
  }

  // 允许只有输入或只有观察结果的工具调用显示
  return true;
};

// 辅助函数：处理thinkingContent以提取工具调用信息
const processThinkingContentForTools = () => {
  if (!hasToolInfoList.value && props.thinkingContent) {
    console.log('Processing thinkingContent for tools...');
    
    // 首先清空现有的工具调用，避免累积
    toolCalls.value = [];
    
    // 处理JSON格式的thinkingContent
    if (typeof props.thinkingContent === 'object' && props.thinkingContent !== null) {
      // 从JSON对象中提取工具调用信息
      if (Array.isArray(props.thinkingContent)) {
        console.log('Processing array thinkingContent');
        
        // 检查是否是agent_thought事件列表
        const isAgentThoughtList = (props.thinkingContent as any[]).some((item: any) =>
          item.event === 'agent_thought' && (item.tool || item.tool_input || (item as any).toll)
        );

        if (isAgentThoughtList) {
          console.log('Processing agent_thought list');
          // 专门处理agent_thought事件列表
          const filteredItems = (props.thinkingContent as any[]).filter((item: any) =>
            (item.tool || (item as any).toll) && (item.tool || (item as any).toll) !== '' && (item.tool || (item as any).toll).trim() !== ''
          );

          const extractedToolCalls = filteredItems.map((item: any) => ({
            name: item.tool || (item as any).toll || '',
            input: item.tool_input || '',
            observation: item.observation || ''
          }));

          if (extractedToolCalls.length > 0) {
            toolCalls.value = extractedToolCalls;
            initializeToolCallCollapsed();
            return;
          }
        }

        // 如果不是agent_thought列表，尝试常规的工具调用数组处理
        const extractedCalls: any[] = [];
        (props.thinkingContent as any[]).forEach((item: any) => {
          if (item.tool || item.tool_input || item.observation || (item as any).toll || item.tool_calls) {
            const toolCall = {
              name: item.name || item.tool || item.tool_name || (item as any).toll || '',
              input: item.tool_input || item.input || (item.tool_calls && item.tool_calls[0]?.input) || '',
              observation: item.observation || ''
            };
            extractedCalls.push(toolCall);
          }
        });
        
        if (extractedCalls.length > 0) {
          toolCalls.value = extractedCalls.filter((call: any) => call.name && call.name.trim() !== '');
          initializeToolCallCollapsed();
          return;
        }
      } else if ((props.thinkingContent as any).tool_calls) {
        // 直接从tool_calls字段提取
        if (Array.isArray((props.thinkingContent as any).tool_calls)) {
          console.log('Processing tool_calls field');
          const extractedCalls = (props.thinkingContent as any).tool_calls.map((call: any) => ({
            name: call.name || call.tool || call.tool_name || '',
            input: call.input || call.tool_input || '',
            observation: call.observation || ''
          }));
          toolCalls.value = extractedCalls.filter((call: any) => call.name && call.name.trim() !== '');
          initializeToolCallCollapsed();
          return;
        }
      } else if ((props.thinkingContent as any).name || (props.thinkingContent as any).tool || (props.thinkingContent as any).toll || (props.thinkingContent as any).tool_input || (props.thinkingContent as any).observation) {
        // 单个工具调用对象
        console.log('Processing single tool call object');
        const toolCall = {
          name: (props.thinkingContent as any).name || (props.thinkingContent as any).tool || (props.thinkingContent as any).tool_name || (props.thinkingContent as any).toll || '',
          input: (props.thinkingContent as any).input || (props.thinkingContent as any).tool_input || '',
          observation: (props.thinkingContent as any).observation || ''
        };

        if (toolCall.name && toolCall.name.trim() !== '') {
          toolCalls.value = [toolCall];
          initializeToolCallCollapsed();
          return;
        }
      }
    } else if (typeof props.thinkingContent === 'string') {
      // 尝试解析字符串为JSON
      try {
        console.log('Trying to parse string as JSON');
        const parsedContent = JSON.parse(props.thinkingContent);
        // 创建临时对象来调用函数
        const tempProps = { ...props, thinkingContent: parsedContent };
        processThinkingContentForTools();
        return;
      } catch (error) {
        console.log('String is not valid JSON:', (error as Error).message);
        // 字符串不是有效的JSON，清空toolCalls
        toolCalls.value = [];
      }
    }

    console.log('No valid tool calls extracted');
  }
};

// 监听toolInfoList变化 - 最高优先级，完全控制工具调用显示
// 添加对toolInfoVersion的监听以确保响应式更新
watch([() => props.toolInfoList, () => props.toolInfoVersion], ([newToolInfoList]) => {
  console.log('toolInfoList changed:', newToolInfoList); // 添加日志检查数据
  // 当toolInfoList有效时，使用其数据并覆盖任何可能存在的工具调用信息
  if (newToolInfoList && Array.isArray(newToolInfoList) && newToolInfoList.length > 0) {
    console.log('Processing toolInfoList with data:', newToolInfoList);
    // 清空并重新构建工具调用数组，确保数据格式一致
    const newToolCalls: any[] = [];

    // 处理每一个工具调用，排除名称为空或为'未命名工具'的情况
    newToolInfoList.forEach((toolInfo, index) => {
      console.log(`Processing toolInfo ${index}:`, toolInfo); // 添加日志检查每个工具调用
      // 安全地处理工具调用数据，避免解析错误
      // 确保input和observation是分开的对象
      const toolCall = {
        name: toolInfo.name || toolInfo.tool || (toolInfo as any).toll || '', // 添加对tool和toll字段的支持
        input: toolInfo.input || toolInfo.tool_input || '', // 添加对tool_input字段的支持
        observation: toolInfo.observation || '' // 确保观察结果存在，即使是空字符串
      };

      console.log(`Processed toolCall ${index}:`, toolCall); // 添加日志检查处理后的工具调用
      
      // 只添加有效的工具调用
      if (toolCall.name && toolCall.name.trim() !== '') {
        newToolCalls.push(toolCall);
      }
    });

    // 更新toolCalls，确保数据完全同步，并对工具调用进行去重
    toolCalls.value = newToolCalls; // 移除去重逻辑方便调试
    console.log('Final toolCalls:', toolCalls.value); // 添加日志检查最终结果
    // 确保所有工具调用的折叠状态都正确初始化
    initializeToolCallCollapsed();
    // 标记已使用toolInfoList
    hasToolInfoList.value = true;
  } else {
    // 当toolInfoList无效时，标记为未使用toolInfoList
    hasToolInfoList.value = false;
    console.log('toolInfoList is empty or invalid');
    // 保留现有toolCalls，避免清空已从thinkingContent提取的数据
    console.log('toolInfoList is empty, keeping existing toolCalls if any');
    initializeToolCallCollapsed();
  }
}, { immediate: true });

// thinkingContent监听器将在下方调用processThinkingContentForTools函数

// 监听thinkingContent变化，从文本中提取工具调用信息作为备用
watch(() => props.thinkingContent, (newThinkingContent) => {
  console.log('thinkingContent changed:', newThinkingContent); // 添加日志检查数据
  // 只有当未使用toolInfoList时，才从thinkingContent中提取工具调用信息
  if (!hasToolInfoList.value) {
    // 调用辅助函数处理thinkingContent
    processThinkingContentForTools();
  }
}, { immediate: true })

// 切换思考过程区域的展开/折叠
const toggleThinkingProcess = () => {
  thinkingProcessCollapsed.value = !thinkingProcessCollapsed.value
}

// 切换思考详情的展开/折叠
const toggleThinkingDetail = () => {
  thinkingDetailCollapsed.value = !thinkingDetailCollapsed.value
}

// 切换工具调用详情的展开/折叠
const toggleToolCallDetail = (index: number) => {
  // 安全检查：确保index在有效范围内
  if (index < 0 || index >= toolCalls.value.length) {
    return;
  }

  // 确保toolCallCollapsed数组长度足够
  while (toolCallCollapsed.value.length <= index) {
    // 默认折叠状态为true
    toolCallCollapsed.value.push(true)
  }

  // 切换指定工具调用的折叠状态
  const newCollapsedState = !toolCallCollapsed.value[index]
  toolCallCollapsed.value.splice(index, 1, newCollapsedState)
}

// 切换其他事件的展开/折叠
const toggleOtherEvents = () => {
  otherEventsCollapsed.value = !otherEventsCollapsed.value
}

// 格式化其他事件数据
const formatOtherEventData = (event: any) => {
  try {
    if (event === null || event === undefined) {
      return 'null';
    }

    if (typeof event === 'object') {
      return JSON.stringify(event, null, 2);
    }

    return String(event);
  } catch (e) {
    return `数据解析错误：${String(event || '无数据')}`;
  }
}

// 获取工具调用图标
const getToolCallIcon = (toolCallItem: any) => {
  // 确保返回有效的图标组件，使用Tools作为默认图标
  return Tools;
}

// 获取工具调用类型的显示名称
const getToolCallType = (toolCall: any) => {
  // 确保toolCall对象有效
  if (!toolCall || typeof toolCall !== 'object') {
    return '工具操作';
  }

  console.log('Processing tool call for type:', toolCall);

  let toolName = toolCall.name || '';

  // 如果没有名称但有input，尝试从input中提取工具名称
  if (!toolName && toolCall.input) {
    if (typeof toolCall.input === 'object') {
      // 尝试从input对象的键中提取工具名称
      if (Array.isArray(toolCall.input)) {
        // 数组类型输入的特殊处理
        if (toolCall.input.length > 0) {
          toolName = 'array_data';
          console.log('Extracted tool name from array input:', toolName);
        }
      } else {
        const inputKeys = Object.keys(toolCall.input);
        if (inputKeys.length > 0) {
          toolName = inputKeys[0];
          console.log('Extracted tool name from object keys:', toolName);
        }
      }
    } else if (typeof toolCall.input === 'string') {
      // 尝试从input字符串中解析出工具名称
      try {
        // 处理字符串中可能包含的JSON对象
        const parsedInput = JSON.parse(toolCall.input);
        if (parsedInput && typeof parsedInput === 'object') {
          const inputKeys = Object.keys(parsedInput);
          if (inputKeys.length > 0) {
            toolName = inputKeys[0];
            console.log('Extracted tool name from parsed JSON:', toolName);
          }
        }
      } catch (e) {
        // 解析失败时，尝试从字符串内容中提取可能的工具名称
        // 处理形如"{"tool_name": {...}}"的情况
        const toolNameMatch = toolCall.input.match(/"([^"]+)":\s*\{/);
        if (toolNameMatch && toolNameMatch.length > 1) {
          toolName = toolNameMatch[1];
          console.log('Extracted tool name from JSON string match:', toolName);
        }

        // 如果仍未找到工具名称，继续尝试其他方法
        if (!toolName) {
          // 处理形如"tool_name: {...}"的情况
          const colonMatch = toolCall.input.match(/^(\w+):\s*/);
          if (colonMatch && colonMatch.length > 1) {
            toolName = colonMatch[1];
            console.log('Extracted tool name from colon format:', toolName);
          }
        }

        // 如果仍未找到工具名称，处理特殊格式
        if (!toolName) {
          if (toolCall.input.includes('[CurrentTime]')) {
            toolName = 'current_time';
          }
          if (toolCall.input.includes('[dataset_')) {
            toolName = 'dataset_query';
          }
          if (toolCall.input.includes('Bill_SaleHeader') || toolCall.input.includes('SaleHeader')) {
            toolName = 'sales_data_query';
          }
        }

        // 如果仍未找到工具名称，检测内容特征
        if (!toolName) {
          // 检测是否包含表格数据特征
          if (toolCall.input.includes('\n') && toolCall.input.includes(',')) {
            toolName = 'table_format';
          }
          // 检测是否包含SQL特征
          if (toolCall.input.toUpperCase().includes('SELECT') ||
            toolCall.input.toUpperCase().includes('FROM') ||
            toolCall.input.toUpperCase().includes('WHERE')) {
            toolName = 'sql_execute';
          }
          // 检测是否包含知识库查询特征
          if (toolCall.input.includes('查询') ||
            toolCall.input.includes('搜索') ||
            toolCall.input.includes('查找')) {
            toolName = 'dataset_query';
          }
        }
      }
    }
  }

  // 更积极的默认名称设置，确保永远不会返回空标题
  if (!toolName || toolName.trim() === '') {
    if (toolCall.observation && toolCall.observation !== '') {
      toolName = '工具调用';
    } else if (toolCall.input && toolCall.input !== '') {
      toolName = '工具请求';
    } else {
      toolName = '工具操作';
    }
    console.log('Used fallback tool name:', toolName);
  }

  // 对于dataset_xxx格式的工具名称，显示为知识库
  if (toolName.startsWith('dataset_') || toolName === 'dataset_query') {
    return '知识库';
  }

  // 对于current_time格式的工具名称，显示为当前时间
  if (toolName === 'current_time') {
    return '当前时间';
  }

  // 对于sql_execute格式的工具名称，显示为SQL执行
  if (toolName === 'sql_execute') {
    return 'SQL执行';
  }

  // 对于bar_chart格式的工具名称，显示为柱状图
  if (toolName === 'bar_chart') {
    return '柱状图';
  }

  // 对于table_format格式的工具名称，显示为表格数据
  if (toolName === 'table_format' || toolName === 'sales_data_query') {
    return '表格数据';
  }

  // 对于array_data格式的工具名称，显示为数组数据
  if (toolName === 'array_data') {
    return '数组数据';
  }

  // 对于其他情况，返回工具名称或默认值
  const finalName = toolName || '工具操作';
  console.log('Final tool name:', finalName);
  return finalName;
}

// 格式化工具调用数据为JSON字符串
const formatToolCallData = (toolCallData: any) => {
  try {
    // 处理所有工具的响应数据的情况（空白工具）
    if (toolCallData && typeof toolCallData === 'object' && toolCallData.all_tools_response) {
      return '所有工具的响应数据';
    }

    // 如果是null或undefined，返回明确的提示
    if (toolCallData === null || toolCallData === undefined) {
      return 'null';
    }

    // 如果是空对象，返回提示信息
    if (typeof toolCallData === 'object' && Object.keys(toolCallData).length === 0) {
      return '空数据';
    }

    // 如果是对象，格式化为JSON字符串，限制最大深度以避免过宽显示
    if (typeof toolCallData === 'object') {
      try {
        // 对于所有类型的对象，统一格式化为JSON字符串
        const jsonStr = JSON.stringify(toolCallData, null, 2);
        if (jsonStr.length > 10000) {
          return jsonStr.substring(0, 10000) + '\n\n... 数据过长，已截断 ...';
        }
        return jsonStr;
      } catch (e) {
        // 处理循环引用等特殊情况
        return `对象序列化失败：${String(toolCallData)}`;
      }
    }

    // 如果是字符串，直接处理字符串内容，不进行trim操作
    else if (typeof toolCallData === 'string') {
      // 检查字符串是否已经是有效的JSON格式
      if ((toolCallData.trim().startsWith('{') && toolCallData.trim().endsWith('}')) ||
        (toolCallData.trim().startsWith('[') && toolCallData.trim().endsWith(']'))) {
        try {
          // 尝试解析并重新格式化
          const parsed = JSON.parse(toolCallData);
          const jsonStr = JSON.stringify(parsed, null, 2);
          if (jsonStr.length > 10000) {
            return jsonStr.substring(0, 10000) + '\n\n... 数据过长，已截断 ...';
          }
          return jsonStr;
        } catch (e) {
          // 如果解析失败，返回原始字符串，但添加提示
          return `数据格式可能不完整或包含特殊字符：\n${toolCallData}`;
        }
      }

      // 尝试从字符串中提取JSON部分（处理类似"参数: {...}"的格式）
      try {
        const jsonMatch = toolCallData.match(/\{.*\}|\[.*\]/s);
        if (jsonMatch && jsonMatch.length > 0) {
          const parsed = JSON.parse(jsonMatch[0]);
          return JSON.stringify(parsed, null, 2);
        }
      } catch (e) {
        // 如果尝试提取失败，继续使用原始数据
      }

      // 检测是否包含类似JSON的格式，但被包裹在其他文本中
      if (toolCallData.includes('{') && toolCallData.includes('}') && toolCallData.includes(':')) {
        try {
          // 找到第一个{和最后一个}，提取JSON部分
          const firstBrace = toolCallData.indexOf('{');
          const lastBrace = toolCallData.lastIndexOf('}');
          if (firstBrace !== -1 && lastBrace !== -1 && firstBrace < lastBrace) {
            const potentialJson = toolCallData.substring(firstBrace, lastBrace + 1);
            const parsed = JSON.parse(potentialJson);
            return JSON.stringify(parsed, null, 2);
          }
        } catch (e) {
          // 如果解析失败，继续处理
        }
      }

      // 对于空字符串，返回提示
      if (toolCallData === '') {
        return '空字符串';
      }

      // 对于可能包含换行符的长字符串，确保正确显示
      // 保留原始换行符，不进行转义，以确保表格数据正确显示
      return toolCallData;
    }

    // 其他类型的数据（数字、布尔值等）
    return String(toolCallData);
  } catch (e) {
    // 如果发生任何错误，返回包含错误信息的原始数据
    console.error('格式化工具调用数据时出错:', e);
    return `数据解析错误：${String(toolCallData || '无数据')}`;
  }
}

// 计算有效的工具调用（名称有效且数据有效）
const validToolCalls = computed(() => {
  // 添加调试日志
  console.log('Tool calls available:', toolCalls.value);
  console.log('Tool calls count:', toolCalls.value.length);
  if (Array.isArray(toolCalls.value)) {
    toolCalls.value.forEach((call, index) => {
      console.log(`Tool call ${index}:`, {
        name: call.name,
        input: call.input ? typeof call.input : 'undefined',
        observation: call.observation ? typeof call.observation : 'undefined'
      });
    });
  }
  
  // 对工具调用进行过滤，只显示有效的工具调用
  // 如果toolCalls.value为空或不是数组，返回空数组
  if (!Array.isArray(toolCalls.value)) {
    return [];
  }
  
  const filteredCalls = toolCalls.value.filter((toolCall: any) => {
    const isValid = isHistoricalValidToolCall(toolCall);
    console.log('Tool call validation result:', toolCall, 'is valid:', isValid);
    return isValid;
  });
  
  console.log('Filtered tool calls:', filteredCalls);
  return filteredCalls;
});

// 检查是否为等待响应状态
const isWaitingResponse = (observation: any): boolean => {
  if (typeof observation === 'string') {
    // 定义等待响应相关的关键词
    const waitingKeywords = ['等待响应', 'loading', 'pending', '等待中'];
    return waitingKeywords.some(keyword =>
      observation.toLowerCase().includes(keyword.toLowerCase()));
  }
  return false;
};

</script>

<style scoped lang="scss">
.thinking-process-container {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 100%;
  position: relative;
  background: #ffffff;
  margin-top: 12px;
}

.events-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  user-select: none;
  position: relative;
  font-size: 14px;
  font-weight: 500;
}

.events-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #4299e1, #9f7aea);
}

.events-icon {
  margin-right: 8px;
  color: #4299e1;
}

.events-title {
  font-weight: 600;
  color: #2d3748;
  margin-right: 8px;
  font-size: 16px;
}

.debug-info {
  color: #e53e3e;
  font-size: 12px;
  margin-left: 8px;
  font-weight: 500;
}

.debug-section {
  margin-top: 12px;
  padding: 8px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}

.debug-title {
  font-size: 12px;
  color: #718096;
  margin-bottom: 4px;
  font-weight: 500;
}

.events-tag {
  margin-right: auto;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
}

.collapse-icon {
  transition: transform 0.3s ease;
  color: #4a5568;

  &.is-collapsed {
    transform: rotate(-90deg);
  }
}

.events-list {
  border-top: 1px solid #e2e8f0;
  max-height: 400px;
  overflow-y: auto;
  background-color: #ffffff;
  border-radius: 0 0 8px 8px;
  border: 1px solid #e2e8f0;
  border-top: none;
}

/* 滚动条样式优化 */
.events-list::-webkit-scrollbar {
  width: 8px;
}

.events-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.events-list::-webkit-scrollbar-thumb {
  background: #4299e1;
  border-radius: 4px;
}

.events-list::-webkit-scrollbar-thumb:hover {
  background: #3182ce;
}

.event-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;

  &:last-child {
    border-bottom: none;
  }

  &.event-thinking {
    border-left: 3px solid #4299e1;
  }

  &.event-tool-call {
    border-left: 3px solid #9f7aea;
  }

  &.event-other-events {
    border-left: 3px solid #48bb78;
  }
}

.event-header {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  cursor: pointer;
  user-select: none;
}

.event-icon {
  margin-right: 8px;
  font-size: 16px;

  .event-thinking & {
    color: #4299e1;
  }

  .event-tool-call & {
    color: #9f7aea;
  }

  .event-other-events & {
    color: #48bb78;
  }
}

.event-type {
  font-weight: 600;
  font-size: 14px;
  flex: 1;

  .event-thinking & {
    color: #4299e1;
  }

  .event-tool-call & {
    color: #7c3aed;
  }

  .event-other-events & {
    color: #38a169;
  }
}

.event-collapse-icon {
  transition: transform 0.3s ease;
  color: #4a5568;
  margin-left: 8px;

  &.is-collapsed {
    transform: rotate(-90deg);
  }
}

.event-message {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.4;
  padding-left: 24px;
  margin-bottom: 8px;
  white-space: pre-wrap;

  &.is-collapsed {
    display: none;
  }
}

.other-event-item {
  margin-bottom: 12px;

  &:last-child {
    margin-bottom: 0;
  }
}

.other-event-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: #4a5568;
  font-size: 12px;
}

.event-raw-data {
  font-size: 12px;
  background-color: #f8fafc;
  border-radius: 4px;
  padding: 8px 12px;
  margin-top: 8px;
  overflow-x: auto;
  /* 限制宽度，确保与AI回复和工作流事件宽度一致 */
  max-width: calc(100vw - 80px);
  box-sizing: border-box;

  &.is-collapsed {
    display: none;
  }

  pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: #2d3748;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    /* 美化JSON数据显示，添加最大宽度限制 */
    max-width: 100%;
    overflow-wrap: break-word;
    word-break: break-all;
  }
}

.tool-section {
  margin-bottom: 12px;

  &:last-child {
    margin-bottom: 0;
  }
}

.tool-section-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: #4a5568;
}

.loading-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-dots {
  display: flex;
  align-items: center;
}

.loading-dots span {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #4a5568;
  margin-left: 4px;
  animation: dot-flashing 1s infinite linear alternate;
  animation-delay: 0s;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.3s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes dot-flashing {
  0% {
    background-color: #4a5568;
  }

  50%,
  100% {
    background-color: #a0aec0;
  }
}

/* 动画 */
.slideFade-enter-active {
  transition: all 0.3s ease;
}

.slideFade-leave-active {
  transition: all 0.3s ease;
}

.slideFade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slideFade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>