<template>
  <div class="message-actions-container">
    <div class="actions-header">
      <h3>消息操作</h3>
      <div class="selection-controls">
        <el-checkbox 
          v-model="selectAll" 
          @change="handleSelectAll"
          class="select-all-checkbox"
        >
          全选
        </el-checkbox>
        <el-button 
          type="primary" 
          link 
          @click="handleInverseSelection"
          class="inverse-selection-btn"
        >
          反选
        </el-button>
      </div>
    </div>
    
    <div class="messages-list">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message-item"
        :class="{ 'selected': selectedMessages.includes(message.id) }"
        @click="toggleMessageSelection(message.id)"
      >
        <el-checkbox 
          :model-value="selectedMessages.includes(message.id)"
          @change="(val: string | number | boolean) => handleCheckboxChange(message.id, val)"
          class="message-checkbox"
        />
        <div class="message-content">
          <div class="message-role" :class="message.role">
            {{ message.role === 'user' ? '用户' : 'AI' }}
          </div>
          <div class="message-text">{{ truncateText(message.content, 100) }}</div>
          <div class="message-time">{{ formatTime(message.created_at) }}</div>
        </div>
      </div>
    </div>
    
    <div class="actions-footer">
      <div class="selected-count">
        已选择 {{ selectedMessages.length }} 条消息
      </div>
      <div class="action-buttons">
        <el-button 
          type="primary" 
          :disabled="selectedMessages.length === 0"
          @click="handleSave"
          class="save-btn"
        >
          保存
        </el-button>
        <el-button 
          type="success" 
          :disabled="selectedMessages.length === 0"
          @click="handleShare"
          class="share-btn"
        >
          分享
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Message {
  id: number
  role: 'user' | 'agent'
  content: string
  created_at: string
}

// Props
const props = defineProps<{
  messages: Message[]
}>()

// Events
const emit = defineEmits<{
  (e: 'save', messages: Message[]): void
  (e: 'share', messages: Message[]): void
}>()

// 选中的消息ID列表
const selectedMessages = ref<number[]>([])

// 全选控制
const selectAll = computed({
  get() {
    return selectedMessages.value.length === props.messages.length && props.messages.length > 0
  },
  set(val: boolean) {
    if (val) {
      selectedMessages.value = props.messages.map(msg => msg.id)
    } else {
      selectedMessages.value = []
    }
  }
})

// 处理全选
const handleSelectAll = (val: boolean) => {
  if (val) {
    selectedMessages.value = props.messages.map(msg => msg.id)
  } else {
    selectedMessages.value = []
  }
}

// 处理反选
const handleInverseSelection = () => {
  const allIds = props.messages.map(msg => msg.id)
  selectedMessages.value = allIds.filter(id => !selectedMessages.value.includes(id))
}

// 切换消息选择
const toggleMessageSelection = (id: number) => {
  const index = selectedMessages.value.indexOf(id)
  if (index > -1) {
    selectedMessages.value.splice(index, 1)
  } else {
    selectedMessages.value.push(id)
  }
}

// 处理复选框变化
const handleCheckboxChange = (id: number, val: boolean | string | number) => {
  const index = selectedMessages.value.indexOf(id)
  if (val && index === -1) {
    selectedMessages.value.push(id)
  } else if (!val && index > -1) {
    selectedMessages.value.splice(index, 1)
  }
}

// 保存消息
const handleSave = () => {
  if (selectedMessages.value.length === 0) {
    ElMessage.warning('请至少选择一条消息')
    return
  }
  
  ElMessageBox.prompt('请输入保存的文件名', '保存消息', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^.+$/,
    inputErrorMessage: '文件名不能为空'
  }).then(({ value }) => {
    // 获取选中的消息
    const selectedMsgs = props.messages.filter(msg => selectedMessages.value.includes(msg.id))
    // 发出保存事件
    emit('save', selectedMsgs)
    ElMessage.success(`成功保存 ${selectedMessages.value.length} 条消息到 ${value}`)
    // 重置选择
    selectedMessages.value = []
  }).catch(() => {
    // 取消操作
  })
}

// 分享消息
const handleShare = () => {
  if (selectedMessages.value.length === 0) {
    ElMessage.warning('请至少选择一条消息')
    return
  }
  
  // 获取选中的消息
  const selectedMsgs = props.messages.filter(msg => selectedMessages.value.includes(msg.id))
  // 发出分享事件
  emit('share', selectedMsgs)
  ElMessage.success(`成功分享 ${selectedMessages.value.length} 条消息`)
  // 重置选择
  selectedMessages.value = []
}

// 工具函数：截断文本
const truncateText = (text: string, length: number): string => {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

// 工具函数：格式化时间
const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped lang="scss">
.message-actions-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 600px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8f9fa, #edf2f7);
  border-radius: 12px 12px 0 0;
}

.actions-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
}

.selection-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.select-all-checkbox {
  margin-right: 0;
  font-weight: 500;
  color: #4a5568;
}

.inverse-selection-btn {
  font-size: 14px;
  padding: 0;
  font-weight: 500;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.message-item {
  display: flex;
  align-items: flex-start;
  padding: 16px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f1f5f9;
}

.message-item:hover {
  background-color: #f8f9fa;
}

.message-item.selected {
  background-color: #ebf8ff;
  border-left: 4px solid #3182ce;
}

.message-checkbox {
  margin-top: 4px;
  margin-right: 16px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-role {
  display: inline-block;
  padding: 4px 10px;
  font-size: 13px;
  border-radius: 20px;
  margin-bottom: 8px;
  font-weight: 600;
}

.message-role.user {
  background-color: #e6fffa;
  color: #0d9488;
  border: 1px solid #0d9488;
}

.message-role.agent {
  background-color: #ede9fe;
  color: #7c3aed;
  border: 1px solid #7c3aed;
}

.message-text {
  font-size: 15px;
  color: #4a5568;
  margin-bottom: 8px;
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
}

.message-time {
  font-size: 13px;
  color: #718096;
  font-style: italic;
}

.actions-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8f9fa, #edf2f7);
  border-radius: 0 0 12px 12px;
}

.selected-count {
  font-size: 15px;
  font-weight: 500;
  color: #4a5568;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.save-btn,
.share-btn {
  padding: 10px 24px;
  font-size: 15px;
  border-radius: 8px;
  font-weight: 500;
}

.save-btn {
  background: linear-gradient(135deg, #3182ce, #2b6cb0);
  border: none;
}

.share-btn {
  background: linear-gradient(135deg, #38a169, #2f855a);
  border: none;
}
</style>