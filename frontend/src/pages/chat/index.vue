<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed, onMounted } from 'vue';
import ChatDefaul from '@/pages/chat/layouts/chatDefaul/index.vue';
import ChatWithId from '@/pages/chat/layouts/chatWithId/index.vue';
import { useUserStore } from '@/stores';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const sessionId = computed(() => route.params?.id);

// 检查用户是否已登录
onMounted(() => {
  if (!userStore.token) {
    router.replace({ name: 'login' });
  }
});
</script>

<template>
  <div class="chat-container">
    <!-- 只有登录用户才能看到聊天界面 -->
    <template v-if="userStore.token">
      <!-- 默认聊天页面 -->
      <ChatDefaul v-if="!sessionId" />
      <!-- 带id的聊天页面 -->
      <ChatWithId v-else />
    </template>
  </div>
</template>

<style lang="scss" scoped>
.chat-container {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow-anchor: none;
}
</style>
