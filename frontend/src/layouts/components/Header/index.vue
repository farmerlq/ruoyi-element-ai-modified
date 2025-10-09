<!-- Header 头部 -->
<script setup lang="ts">
import { ChatLineSquare } from '@element-plus/icons-vue';
import { onKeyStroke } from '@vueuse/core';
import { computed, onMounted } from 'vue';
import { SIDE_BAR_WIDTH } from '@/config/index';
import { useDesignStore, useUserStore } from '@/stores';
import { useSessionStore } from '@/stores/modules/session';
import { useChatStore } from '@/stores/modules/chat';
import Collapse from './components/Collapse.vue';
import CreateChat from './components/CreateChat.vue';
import LoginBtn from './components/LoginBtn.vue';
import TitleEditing from './components/TitleEditing.vue';
import { useRoute } from 'vue-router';


const userStore = useUserStore();
const designStore = useDesignStore();
const sessionStore = useSessionStore();
const chatStore = useChatStore();
const route = useRoute();

const currentSession = computed(() => sessionStore.currentSession);

onMounted(() => {
  // 全局设置侧边栏默认宽度 (这个是不变的，一开始就设置)
  document.documentElement.style.setProperty(`--sidebar-default-width`, `${SIDE_BAR_WIDTH}px`);
  if (designStore.isCollapse) {
    document.documentElement.style.setProperty(`--sidebar-left-container-default-width`, ``);
  }
  else {
    document.documentElement.style.setProperty(
      `--sidebar-left-container-default-width`,
      `${SIDE_BAR_WIDTH}px`,
    );
  }
});

// 定义 Ctrl+K 的处理函数
function handleCtrlK(event: KeyboardEvent) {
  event.preventDefault(); // 防止默认行为
  sessionStore.createSessionBtn();
}

// 设置全局的键盘按键监听
onKeyStroke(event => event.ctrlKey && event.key.toLowerCase() === 'k', handleCtrlK, {
  passive: false,
});

// 处理消息操作功能
function handleMessageActions() {
  // 触发事件，让聊天页面打开消息操作抽屉
  window.dispatchEvent(new CustomEvent('open-message-actions'));
}
</script>

<template>
  <div class="header-container">
    <div class="header-box">
      <div class="header-content">
        <div class="left-section">
          <div
            v-if="designStore.isCollapse"
            class="left-box"
          >
            <Collapse />
            <CreateChat />
            <div v-if="currentSession" class="divider" />
          </div>

          <div class="middle-box">
            <TitleEditing />
          </div>
        </div>

        <div class="right-section">
          <div v-if="userStore.token" class="action-icons">
            <el-icon class="icon-btn" @click="handleMessageActions">
              <ChatLineSquare />
            </el-icon>
          </div>
          <LoginBtn v-show="!userStore.token" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.header-container {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  width: 100%;
  height: fit-content;
}

.header-box {
  width: calc(100% - var(--sidebar-left-container-default-width, 0px));
  height: var(--header-container-default-heigth);
  margin-left: var(--sidebar-left-container-default-width, 0);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  padding: 0 20px;
  box-sizing: border-box;
}

.left-section {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.left-box {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.divider {
  width: 0.5px;
  height: 30px;
  background-color: rgba(217, 217, 217, 1);
}

.middle-box {
  flex: 1;
  min-width: 0;
  margin-left: 12px;
  overflow: hidden;
}

.right-section {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  margin-left: 12px;
}

.action-icons {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.icon-btn {
  font-size: 18px;
  color: #666666;
  cursor: pointer;
  transition: color 0.3s ease;
  margin-left: 12px;
}

.icon-btn:first-child {
  margin-left: 0;
}

.icon-btn:hover {
  color: #333333;
}

@media (max-width: 768px) {
  .left-box {
    gap: 8px;
  }
  
  .middle-box {
    margin-left: 8px;
  }
  
  .right-section {
    margin-left: 8px;
  }
  
  .icon-btn {
    margin-left: 8px;
  }
  
  .header-content {
    padding: 0 12px;
  }
}
</style>