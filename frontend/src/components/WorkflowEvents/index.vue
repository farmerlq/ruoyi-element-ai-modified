<!-- 工作流事件组件 -->
<template>
  <div class="workflow-events-container">
    <div 
      v-if="workflowEvents && workflowEvents.length > 0" 
      class="workflow-events-content"
    >
      <div class="events-header" @click="toggleCollapse">
        <el-icon class="events-icon"><Collection /></el-icon>
        <span class="events-title">工作流执行过程</span>
        <el-tag type="info" size="small" class="events-tag">点击展开/收起</el-tag>
        <el-icon class="collapse-icon" :class="{ 'is-collapsed': isCollapsed }">
          <ArrowDown />
        </el-icon>
      </div>
      
      <transition name="slideFade">
        <div v-show="!isCollapsed" class="events-list">
          <div 
            v-for="(event, index) in workflowEvents" 
            :key="index"
            class="event-item"
            :class="getEventClass(event)"
          >
            <div class="event-header" @click="toggleEventDetail(index)">
              <el-icon class="event-icon">
                <component :is="getEventIcon(event)" />
              </el-icon>
              <span class="event-type">{{ formatEventType(event) }}</span>
              <span class="event-time" v-if="event.data?.created_at || event.data?.finished_at">
                {{ formatEventTime(event) }}
              </span>
              <el-icon class="event-collapse-icon" :class="{ 'is-collapsed': eventCollapsed[index] }">
                <ArrowDown />
              </el-icon>
            </div>
            <div class="event-content" :class="{ 'is-collapsed': eventCollapsed[index] }">
              <div class="event-message" v-if="event.message">
                {{ event.message }}
              </div>
              <div class="event-raw-data">
                <pre>{{ formatEventData(event) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  Collection, 
  ArrowDown,
  InfoFilled,
  SuccessFilled,
  Warning,
  CircleClose,
  Timer,
  DataAnalysis
} from '@element-plus/icons-vue'

const props = defineProps<{
  workflowEvents: any[]
}>()

const isCollapsed = ref(true)
const eventCollapsed = ref<boolean[]>([])

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleEventDetail = (index: number) => {
  // 确保eventCollapsed数组长度足够
  while (eventCollapsed.value.length <= index) {
    eventCollapsed.value.push(false)
  }
  
  // 切换指定事件的折叠状态
  const newCollapsedState = !eventCollapsed.value[index]
  eventCollapsed.value.splice(index, 1, newCollapsedState)
}

// 格式化事件数据为JSON字符串
const formatEventData = (event: any) => {
  try {
    return JSON.stringify(event, null, 2)
  } catch (e) {
    return JSON.stringify({
      error: '无法格式化事件数据',
      raw: event?.toString() || '无数据'
    }, null, 2)
  }
}

// 当工作流事件更新时，重置折叠状态
// watch(
//   () => props.workflowEvents,
//   (newEvents) => {
//     if (newEvents && newEvents.length > 0) {
//       eventCollapsed.value = new Array(newEvents.length).fill(false)
//     }
//   },
//   { immediate: true }
// )

const getEventClass = (event: any) => {
  const eventType = event.type || event.event || 'unknown'
  return `event-${eventType.replace(/_/g, '-')}`
}

const getEventIcon = (event: any) => {
  const eventType = event.type || event.event || 'unknown'
  
  switch (eventType) {
    case 'workflow_started':
      return 'InfoFilled'
    case 'workflow_finished':
      return 'SuccessFilled'
    case 'node_started':
      return 'Timer'
    case 'node_finished':
      return 'SuccessFilled'
    case 'statistics':
      return 'DataAnalysis'
    case 'error':
      return 'CircleClose'
    default:
      return 'InfoFilled'
  }
}

const formatEventType = (event: any) => {
  const eventType = event.type || event.event || 'unknown'
  
  switch (eventType) {
    case 'workflow_started':
      return '工作流开始'
    case 'workflow_finished':
      return '工作流完成'
    case 'node_started':
      return '节点开始'
    case 'node_finished':
      return '节点完成'
    case 'statistics':
      return '统计信息'
    case 'message_end':
      return '消息结束'
    case 'error':
      return '错误事件'
    default:
      return eventType
  }
}

const formatEventTime = (event: any) => {
  // 简化时间显示逻辑
  return ''
}

const shouldShowDetails = (event: any) => {
  const eventType = event.type || event.event || 'unknown'
  // 对于某些事件类型显示详细信息
  return ['statistics', 'workflow_finished', 'error'].includes(eventType)
}

const getEventDetails = (event: any) => {
  const data = event.data || {}
  const details: Record<string, any> = {}
  
  // 根据事件类型提取相关详细信息
  if (data.total_tokens !== undefined) {
    details.total_tokens = data.total_tokens
  }
  if (data.total_tokens_estimated !== undefined) {
    details.total_tokens_estimated = data.total_tokens_estimated
  }
  if (data.estimated_cost !== undefined) {
    details.estimated_cost = data.estimated_cost
  }
  if (data.elapsed_time !== undefined) {
    details.elapsed_time = data.elapsed_time
  }
  if (data.total_steps !== undefined) {
    details.total_steps = data.total_steps
  }
  if (data.status) {
    details.status = data.status
  }
  
  return details
}

const formatDetailKey = (key: string) => {
  const keyMap: Record<string, string> = {
    total_tokens: '总Token数',
    total_tokens_estimated: '估算Token数',
    estimated_cost: '估算费用',
    elapsed_time: '耗时',
    total_steps: '总步骤数',
    status: '状态'
  }
  
  return keyMap[key] || key
}

const formatDetailValue = (value: any) => {
  if (typeof value === 'number') {
    if (value.toString().includes('.')) {
      return value.toFixed(6)
    }
    return value
  }
  return value
}
</script>

<style scoped lang="scss">
.workflow-events-container {
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
  
  &.event-workflow-started {
    border-left: 3px solid #4299e1;
  }
  
  &.event-workflow-finished {
    border-left: 3px solid #48bb78;
  }
  
  &.event-node-started {
    border-left: 3px solid #ed8936;
  }
  
  &.event-node-finished {
    border-left: 3px solid #48bb78;
  }
  
  &.event-statistics {
    border-left: 3px solid #9f7aea;
  }
  
  &.event-error {
    border-left: 3px solid #e53e3e;
    background-color: #fef2f2;
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
  
  .event-workflow-started & {
    color: #4299e1;
  }
  
  .event-workflow-finished & {
    color: #48bb78;
  }
  
  .event-node-started & {
    color: #ed8936;
  }
  
  .event-node-finished & {
    color: #48bb78;
  }
  
  .event-statistics & {
    color: #9f7aea;
  }
  
  .event-error & {
    color: #e53e3e;
  }
}

.event-type {
  font-weight: 600;
  font-size: 14px;
  flex: 1;
  
  .event-workflow-started & {
    color: #4299e1;
  }
  
  .event-workflow-finished & {
    color: #48bb78;
  }
  
  .event-node-started & {
    color: #ed8936;
  }
  
  .event-node-finished & {
    color: #48bb78;
  }
  
  .event-statistics & {
    color: #9f7aea;
  }
  
  .event-error & {
    color: #e53e3e;
  }
}

.event-time {
  font-size: 12px;
  color: #718096;
}

.event-collapse-icon {
  transition: transform 0.3s ease;
  color: #4a5568;
  margin-left: 8px;
  
  &.is-collapsed {
    transform: rotate(-90deg);
  }
}

.event-content {
  &.is-collapsed {
    display: none;
  }
}

.event-message {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.4;
  padding-left: 24px;
  margin-bottom: 8px;
}

.event-raw-data {
  font-size: 12px;
  background-color: #f8fafc;
  border-radius: 4px;
  padding: 8px 12px;
  margin-top: 8px;
  overflow-x: auto;
  
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