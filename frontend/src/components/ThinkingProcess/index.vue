<!-- 思考过程组件 -->
<template>
  <div class="thinking-process-container">
    <div 
      v-if="thinkingContent || (toolInfo && Object.keys(toolInfo).length > 0)" 
      class="thinking-process-content"
    >
      <div class="events-header" @click="toggleCollapse">
        <el-icon class="events-icon"><Collection /></el-icon>
        <span class="events-title">AI 思考过程</span>
        <el-tag type="info" size="small" class="events-tag">点击展开/收起</el-tag>
        <el-icon class="collapse-icon" :class="{ 'is-collapsed': isCollapsed }">
          <ArrowDown />
        </el-icon>
      </div>
      
      <transition name="slideFade">
        <div v-show="!isCollapsed" class="events-list">
          <div class="event-item event-thinking">
            <div class="event-header" @click="toggleThinkingDetail">
              <el-icon class="event-icon">
                <InfoFilled />
              </el-icon>
              <span class="event-type">思考过程</span>
              <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': thinkingCollapsed }">
                <ArrowDown />
              </el-icon>
            </div>
            <div v-if="thinkingContent" class="event-message" :class="{ 'is-collapsed': thinkingCollapsed }">
              {{ thinkingContent }}
            </div>
          </div>
          
          <!-- 工具调用信息 -->
          <div 
            v-for="(toolCall, index) in toolCalls" 
            :key="index"
            class="event-item event-tool-call"
          >
            <div class="event-header" @click="toggleToolCallDetail(index)">
              <el-icon class="event-icon">
                <component :is="getToolCallIcon(toolCall)" />
              </el-icon>
              <span class="event-type">{{ getToolCallType(toolCall) }}</span>
              <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': toolCallCollapsed[index] }">
                <ArrowDown />
              </el-icon>
            </div>
            <div class="event-raw-data" :class="{ 'is-collapsed': toolCallCollapsed[index] }">
              <pre>{{ formatToolCallData(toolCall) }}</pre>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  Collection, 
  ArrowDown,
  InfoFilled,
  SetUp,
  Tools
} from '@element-plus/icons-vue'

const props = defineProps<{
  thinkingContent: string,
  toolInfo?: {
    name: string,
    input: string,
    observation: string
  }
}>()

const isCollapsed = ref(false)
const thinkingCollapsed = ref(false)
const toolCallCollapsed = ref<boolean[]>([])

// 将单个toolInfo转换为工具调用数组
const toolCalls = ref<any[]>([])

// 监听toolInfo变化
if (props.toolInfo && Object.keys(props.toolInfo).length > 0) {
  try {
    const toolCall = {
      name: props.toolInfo.name,
      input: typeof props.toolInfo.input === 'string' ? JSON.parse(props.toolInfo.input) : props.toolInfo.input,
      observation: typeof props.toolInfo.observation === 'string' ? JSON.parse(props.toolInfo.observation) : props.toolInfo.observation
    }
    toolCalls.value = [toolCall]
  } catch (e) {
    // 如果解析失败，使用原始数据
    toolCalls.value = [props.toolInfo]
  }
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleThinkingDetail = () => {
  thinkingCollapsed.value = !thinkingCollapsed.value
}

const toggleToolCallDetail = (index: number) => {
  // 确保toolCallCollapsed数组长度足够
  while (toolCallCollapsed.value.length <= index) {
    toolCallCollapsed.value.push(false)
  }
  
  // 切换指定工具调用的折叠状态
  const newCollapsedState = !toolCallCollapsed.value[index]
  toolCallCollapsed.value.splice(index, 1, newCollapsedState)
}

const getToolCallIcon = (toolCall: any) => {
  return 'Tools'
}

const getToolCallType = (toolCall: any) => {
  return toolCall.name || '工具调用'
}

// 格式化工具调用数据为JSON字符串
const formatToolCallData = (toolCall: any) => {
  try {
    return JSON.stringify(toolCall, null, 2)
  } catch (e) {
    return JSON.stringify({
      error: '无法格式化工具调用数据',
      raw: toolCall?.toString() || '无数据'
    }, null, 2)
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
    color: #9f7aea;
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
  
  &.is-collapsed {
    display: none;
  }
  
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: #2d3748;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
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