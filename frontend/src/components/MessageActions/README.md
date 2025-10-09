# 消息操作组件 (MessageActions)

该组件提供了一个用于保存和分享聊天消息的界面，支持复选、全选和反选功能。

## 功能特性

1. **消息选择**
   - 支持单个消息选择/取消选择
   - 全选功能
   - 反选功能

2. **操作功能**
   - 保存选中的消息
   - 分享选中的消息

3. **用户界面**
   - 清晰的视觉反馈
   - 响应式设计
   - 显示选中消息数量

## 使用方法

```vue
<template>
  <MessageActions 
    :messages="chatMessages" 
    @save="handleSave"
    @share="handleShare"
  />
</template>

<script setup>
import MessageActions from '@/components/MessageActions/index.vue'
import { ref } from 'vue'

const chatMessages = ref([
  {
    id: 1,
    role: 'user',
    content: '你好，我想了解一下产品信息',
    created_at: '2023-01-01T12:00:00Z'
  },
  {
    id: 2,
    role: 'agent',
    content: '您好！很高兴为您服务。我们的产品具有以下特点...',
    created_at: '2023-01-01T12:01:00Z'
  }
])

const handleSave = (messages) => {
  // 处理保存逻辑
  console.log('保存消息:', messages)
}

const handleShare = (messages) => {
  // 处理分享逻辑
  console.log('分享消息:', messages)
}
</script>
```

## Props

| 属性名 | 类型 | 必需 | 描述 |
|-------|------|------|------|
| messages | Array<Message> | 是 | 要显示和操作的消息列表 |

### Message 对象结构

```typescript
interface Message {
  id: number
  role: 'user' | 'agent'
  content: string
  created_at: string
}
```

## 事件

该组件目前不发出事件，所有操作都在组件内部处理。可以通过修改组件来添加事件支持。

## 样式定制

组件使用 SCSS 编写，可以通过覆盖 CSS 变量或直接修改样式来自定义外观。

## 注意事项

1. 组件内部管理选中状态
2. 保存和分享操作会重置选中状态
3. 组件最大高度为 600px，超出部分可滚动