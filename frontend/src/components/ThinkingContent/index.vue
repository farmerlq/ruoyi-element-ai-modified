<template>
  <div 
    v-if="thinkingContent || (toolCalls && toolCalls.length > 0)"
    class="thinking-process-container"
  >
    <div 
      class="events-header" 
      @click="toggleThinkingProcess"
    >
      <el-icon class="events-icon"><Collection /></el-icon>
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
          <div v-if="thinkingContent" class="event-message" :class="{ 'is-collapsed': thinkingDetailCollapsed }">
            {{ thinkingContent }}
          </div>
        </div>
        
        <!-- 工具调用信息 -->
        <div 
          v-for="(toolCall, index) in toolCalls" 
          :key="`${toolCall.name}-${JSON.stringify(toolCall.input).slice(0, 50)}`"
          class="event-item event-tool-call"
        >
          <div class="event-header" @click="toggleToolCallDetail(index)">
            <el-icon class="event-icon">
              <component :is="getToolCallIcon(toolCall)" />
            </el-icon>
            <span class="event-type">使用工具 {{ getToolCallType(toolCall) }}</span>
            <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': toolCallCollapsed[index] }">
              <ArrowDown />
            </el-icon>
          </div>
          <div class="event-raw-data" :class="{ 'is-collapsed': toolCallCollapsed[index] }">
            <div class="tool-section">
              <div class="tool-section-title">请求:</div>
              <pre>{{ formatToolCallData(toolCall.input) }}</pre>
            </div>
            <div v-if="toolCall.observation" class="tool-section">
              <div class="tool-section-title">响应:</div>
              <pre>{{ toolCall.observation }}</pre>
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
  thinkingContent?: string | object | Array<any>
  toolInfoList?: Array<{
    name: string
    input: string
    observation: string
  }>
}>()

// AI思考过程相关状态
const thinkingProcessCollapsed = ref(false)
const thinkingDetailCollapsed = ref(false)
// 工具调用数组
const toolCalls = ref<any[]>([])

// 工具调用折叠状态数组，默认为true（折叠）
const toolCallCollapsed = ref<Array<boolean>>([])

// 初始化时确保所有现有的工具调用都是折叠状态
const initializeToolCallCollapsed = () => {
  if (toolCalls.value.length > 0) {
    // 确保toolCallCollapsed数组长度与toolCalls一致
    while (toolCallCollapsed.value.length < toolCalls.value.length) {
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

// 从thinkingContent文本中提取工具调用信息
const extractToolCallsFromText = (text: string): any[] => {
  const toolCalls: any[] = [];
  if (!text) return toolCalls;
  
  // 匹配[工具调用: tool_name]格式的文本
  const toolCallRegex = /\[工具调用:\s*([^\]]+)\]\s*参数:\s*([\s\S]*?)(?=\n\n\[工具调用:|\n\[|$)/g;
  let match;
  
  while ((match = toolCallRegex.exec(text)) !== null) {
    const toolName = match[1].trim();
    const paramsText = match[2].trim();
    
    try {
      // 尝试解析参数为JSON
      let params = safelyParseJSON(paramsText);
      
      // 如果解析后的参数是字符串，再次尝试解析
      if (typeof params === 'string') {
        params = safelyParseJSON(params);
      }
      
      // 创建工具调用对象
      const toolCall = {
        name: toolName || '未命名工具',
        input: params,
        observation: ''
      };
      
      toolCalls.push(toolCall);
    } catch (e) {
      // 如果解析失败，使用原始参数文本
      toolCalls.push({
        name: toolName || '未命名工具',
        input: paramsText,
        observation: ''
      });
    }
  }
  
  return toolCalls;
};

// 监听toolInfoList变化
watch(() => props.toolInfoList, (newToolInfoList) => {
  // 无论新数据是否有效，都进行处理，确保历史数据和实时数据格式一致
  if (newToolInfoList && Array.isArray(newToolInfoList) && newToolInfoList.length > 0) {
    // 清空并重新构建工具调用数组，确保数据格式一致
    const newToolCalls: any[] = [];
    
    // 处理每一个工具调用
    newToolInfoList.forEach(toolInfo => {
      if (toolInfo) {
        // 安全地处理工具调用数据，避免解析错误
        const toolCall = {
          name: toolInfo.name || '未命名工具',
          input: safelyParseJSON(toolInfo.input),
          observation: safelyParseJSON(toolInfo.observation)
        };
        
        // 添加新的工具调用到临时数组中
        newToolCalls.push(toolCall);
      }
    });
    
    // 更新toolCalls，确保数据完全同步
    toolCalls.value = newToolCalls;
    // 确保所有工具调用的折叠状态都正确初始化
    initializeToolCallCollapsed();
  } else if (!props.thinkingContent || (!toolCalls.value || toolCalls.value.length === 0)) {
    // 只有当thinkingContent不存在且toolCalls为空时，才清空工具调用数组
    // 这样可以避免与thinkingContent监听器冲突
    toolCalls.value = [];
    toolCallCollapsed.value = [];
  }
}, { immediate: true })

// 监听thinkingContent变化，从文本中提取工具调用信息作为备用
watch(() => props.thinkingContent, (newThinkingContent) => {
  // 只有当toolInfoList不存在、不是数组或为空数组，并且toolCalls数组为空时，才从thinkingContent中提取工具调用信息
  // 这样可以避免同时从toolInfoList和thinkingContent提取导致的重复显示
  // 对于agent_thought事件列表，我们需要特殊处理以避免重复显示
  if ((!props.toolInfoList || !Array.isArray(props.toolInfoList) || props.toolInfoList.length === 0) && (!toolCalls.value || toolCalls.value.length === 0)) {
    // 处理JSON格式的thinkingContent
    if (typeof newThinkingContent === 'object' && newThinkingContent !== null) {
      // 从JSON对象中提取工具调用信息
      if (Array.isArray(newThinkingContent)) {
        // 检查是否是agent_thought事件列表
        const isAgentThoughtList = newThinkingContent.some((item: any) => 
          item.event === 'agent_thought' && (item.tool || item.tool_input)
        );
        
        if (isAgentThoughtList) {
          // 专门处理agent_thought事件列表
          // 1. 过滤有效的工具调用，只包含有observation的完整工具调用
          // 2. 或者如果没有observation，确保不与后续可能的完整调用重复
          const hasCompleteToolCalls = newThinkingContent.some((item: any) => 
            item.tool && item.tool !== '' && item.observation && item.observation !== ''
          );
          
          const filteredItems = hasCompleteToolCalls
            // 如果有完整的工具调用，只使用那些有observation的
            ? newThinkingContent.filter((item: any) => 
                item.tool && item.tool !== '' && item.observation && item.observation !== ''
              )
            // 否则使用所有有效工具调用
            : newThinkingContent.filter((item: any) => item.tool && item.tool !== '');
          
          const extractedToolCalls = filteredItems.map((item: any) => ({
            name: item.tool, // 使用tool字段作为工具名称
            input: safelyParseJSON(item.tool_input) || item.tool_input, // 解析tool_input
            observation: safelyParseJSON(item.observation) || item.observation || '' // 解析observation
          }));
          
          if (extractedToolCalls.length > 0) {
            toolCalls.value = extractedToolCalls;
            initializeToolCallCollapsed();
            return;
          }
        }
        
        // 如果不是agent_thought列表，尝试常规的工具调用数组处理
        const extractedToolCalls = newThinkingContent.map((call: any) => ({
          name: call.name || call.tool_name || '未命名工具',
          input: call.input || call.parameters || '',
          observation: call.observation || ''
        }));
        if (extractedToolCalls.length > 0) {
          toolCalls.value = extractedToolCalls;
          initializeToolCallCollapsed();
        }
      } else {
        // 类型断言，告诉TypeScript这个对象有tool_calls属性
        const thinkingContentWithToolCalls = newThinkingContent as { tool_calls?: any[] };
        if (thinkingContentWithToolCalls.tool_calls && Array.isArray(thinkingContentWithToolCalls.tool_calls)) {
          // 从tool_calls字段提取工具调用
          const extractedToolCalls = thinkingContentWithToolCalls.tool_calls.map((call: any) => ({
            name: call.name || call.tool_name || '未命名工具',
            input: call.input || call.parameters || '',
            observation: call.observation || ''
          }));
          if (extractedToolCalls.length > 0) {
            toolCalls.value = extractedToolCalls;
            initializeToolCallCollapsed();
          }
        }
      }
    } else {
      // 从thinkingContent文本中提取工具调用信息
      const extractedToolCalls = extractToolCallsFromText(newThinkingContent || '');
      if (extractedToolCalls.length > 0) {
        toolCalls.value = extractedToolCalls;
        initializeToolCallCollapsed();
      }
    }
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

// 获取工具调用图标
const getToolCallIcon = (toolCall: any) => {
  return 'Tools'
}

// 获取工具调用类型
const getToolCallType = (toolCall: any) => {
  // 确保toolCall对象有效
  if (!toolCall || typeof toolCall !== 'object') {
    return '未命名工具';
  }
  
  let toolName = toolCall.name || '';
  
  // 如果没有名称但有input，尝试从input中提取工具名称
  if (!toolName && toolCall.input) {
    if (typeof toolCall.input === 'object') {
      // 尝试从input对象的键中提取工具名称
      if (Array.isArray(toolCall.input)) {
        // 数组类型输入的特殊处理
        if (toolCall.input.length > 0) {
          toolName = 'array_data';
        }
      } else {
        const inputKeys = Object.keys(toolCall.input);
        if (inputKeys.length > 0) {
          toolName = inputKeys[0];
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
          }
        }
      } catch (e) {
        // 解析失败时，尝试从字符串内容中提取可能的工具名称
        // 处理形如"{"tool_name": {...}}"的情况
        const toolNameMatch = toolCall.input.match(/"([^"]+)":\s*\{/);
        if (toolNameMatch && toolNameMatch.length > 1) {
          toolName = toolNameMatch[1];
        }
        
        // 如果仍未找到工具名称，继续尝试其他方法
        if (!toolName) {
          // 处理形如"tool_name: {...}"的情况
          const colonMatch = toolCall.input.match(/^(\w+):\s*/);
          if (colonMatch && colonMatch.length > 1) {
            toolName = colonMatch[1];
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
        
        // 对于实时数据，确保有默认工具名称，避免空标题
        if (!toolName) {
          toolName = '未命名工具';
        }
      }
    }
  }
  
  // 确保工具名称不为空
  toolName = toolName || '未命名工具';
  
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
  
  // 对于table_format格式的工具名称，显示为表格格式化
  if (toolName === 'table_format' || toolName === 'sales_data_query') {
    return '表格数据';
  }
  
  // 对于array_data格式的工具名称，显示为数组数据
  if (toolName === 'array_data') {
    return '数组数据';
  }
  
  // 对于其他情况，返回工具名称或默认值
  return toolName || '未命名工具';
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
        // 特殊处理特定类型的工具数据
        // 检查对象是否有current_time字段
        if ('current_time' in toolCallData && typeof toolCallData.current_time === 'object') {
          // current_time工具可能没有参数，直接返回友好提示
          if (Object.keys(toolCallData.current_time).length === 0) {
            return '{"current_time": {}}';
          }
        }
        
        // 检查对象是否有dataset_xxx格式的字段
        for (const key in toolCallData) {
          if (key.startsWith('dataset_')) {
            // 确保dataset的参数被正确格式化
            if (toolCallData[key] && typeof toolCallData[key] === 'object' && toolCallData[key].query) {
              // 保留原始格式，但确保正确显示
              return JSON.stringify(toolCallData, null, 2);
            }
          }
        }
        
        // 检查对象是否有sql_execute字段
        if ('sql_execute' in toolCallData && typeof toolCallData.sql_execute === 'object' && toolCallData.sql_execute.query) {
          // 对于SQL查询，确保SQL语句格式正确显示
          const sqlData = {
            sql_execute: {
              query: toolCallData.sql_execute.query
            }
          };
          return JSON.stringify(sqlData, null, 2);
        }
        
        // 检查对象是否有bar_chart字段
        if ('bar_chart' in toolCallData && typeof toolCallData.bar_chart === 'object') {
          // 对于柱状图数据，确保所有字段都被正确显示
          const chartData = {
            bar_chart: {
              title: toolCallData.bar_chart.title || '未命名图表',
              data: toolCallData.bar_chart.data || '',
              x_axis: toolCallData.bar_chart.x_axis || ''
            }
          };
          return JSON.stringify(chartData, null, 2);
        }
        
        // 对于table_format格式的数据，进行特殊处理
        if ('table_format' in toolCallData && typeof toolCallData.table_format === 'object') {
          return JSON.stringify(toolCallData.table_format, null, 2);
        }
        
        // 对于包含表格数据的对象，确保正确格式化显示
        // 检查对象是否包含典型的表格数据结构
        if (toolCallData.data && Array.isArray(toolCallData.data) && toolCallData.data.length > 0) {
          return JSON.stringify(toolCallData, null, 2);
        }
        
        // 对于其他类型的对象，格式化为JSON字符串，限制最大深度以避免过宽显示
        // 对于可能包含大量数据的对象，限制显示长度
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
    
    // 如果是字符串
    else if (typeof toolCallData === 'string') {
      // 检查字符串是否已经是有效的JSON格式
      if ((toolCallData.startsWith('{') && toolCallData.endsWith('}')) ||
          (toolCallData.startsWith('[') && toolCallData.endsWith(']'))) {
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
      
      // 处理从截图中观察到的特殊格式，如包含[CurrentTime]、[dataset_xxx]等
      if (toolCallData.includes('[CurrentTime]')) {
        return '当前时间查询';
      } else if (toolCallData.includes('[dataset_')) {
        return '知识库查询';
      } else if (toolCallData.includes('Bill_SaleHeader') || toolCallData.includes('SaleHeader')) {
        // 尝试格式化表格数据，使其更易读
        try {
          // 检测是否为CSV或类似表格格式的字符串
          if (toolCallData.includes('\n') && toolCallData.includes(',')) {
            // 表格数据格式化，确保美观显示
            const lines = toolCallData.split('\n');
            if (lines.length > 1) {
              // 对于表格数据，确保完整显示表头，并适当截断内容
              const header = lines[0];
              const contentLines = lines.slice(1);
              
              // 如果内容行过多，只显示部分
              if (contentLines.length > 10) {
                return header + '\n' + contentLines.slice(0, 8).join('\n') + '\n...\n' + contentLines.slice(-2).join('\n');
              }
              return toolCallData;
            }
          }
        } catch (e) {
          // 如果格式化失败，返回原始数据
        }
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
      
      // 如果是空字符串，返回提示
      if (toolCallData.trim() === '') {
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

