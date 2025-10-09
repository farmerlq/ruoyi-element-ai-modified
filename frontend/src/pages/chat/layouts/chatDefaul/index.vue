<!-- 默认消息列表页 -->
<script setup lang="ts">
import type { FilesCardProps } from 'vue-element-plus-x/types/FilesCard';
import { Attachments, Sender } from 'vue-element-plus-x';
import { useRouter } from 'vue-router';
import { onMounted, ref, watch, nextTick } from 'vue';
import AgentSelect from '@/components/AgentSelect/index.vue';
import FilesSelect from '@/components/FilesSelect/index.vue';
import WelecomeText from '@/components/WelecomeText/index.vue';
import { useUserStore } from '@/stores';
import { useAgentStore } from '@/stores/modules/agent';
import { useFilesStore } from '@/stores/modules/files';
import { useSessionStore } from '@/stores/modules/session';

const router = useRouter();
const userStore = useUserStore();
const sessionStore = useSessionStore();
const filesStore = useFilesStore();
const agentStore = useAgentStore();

// 检查用户是否已登录
onMounted(() => {
  if (!userStore.token) {
    router.replace({ name: 'login' });
  }
});

const senderValue = ref('');
const senderRef = ref();

async function handleSend() {
  // 确保用户已登录
  if (!userStore.token) {
    router.replace({ name: 'login' });
    return;
  }

  localStorage.setItem('chatContent', senderValue.value);

  await sessionStore.createSessionList({
    user_id: userStore.userInfo?.user_id as number,
    agent_id: agentStore.currentAgentInfo?.id as number,
    merchant_id: userStore.userInfo?.merchant_id as number, // 从用户信息获取商户ID，而不是智能体信息
    title: senderValue.value.slice(0, 10) || '新会话',
    status: 'active',
  });
}
function handleDeleteCard(_item: FilesCardProps, index: number) {
  filesStore.deleteFileByIndex(index);
}

watch(
  () => filesStore.filesList.length,
  (val) => {
    if (val > 0) {
      nextTick(() => {
        senderRef.value.openHeader();
      });
    }
    else {
      nextTick(() => {
        senderRef.value.closeHeader();
      });
    }
  },
);
</script>

<template>
  <div v-if="userStore.token" class="chat-defaul-wrap">
    <WelecomeText />
    <Sender
      ref="senderRef"
      v-model="senderValue"
      class="chat-defaul-sender"
      :auto-size="{
        maxRows: 9,
        minRows: 3,
      }"
      variant="updown"
      clearable
      allow-speech
      @submit="handleSend"
    >
      <template #header>
        <div class="sender-header p-12px pt-6px pb-0px">
          <Attachments
            :items="filesStore.filesList.map(fileItem => fileItem as FilesCardProps)"
            :hide-upload="true"
            @delete-card="handleDeleteCard"
          >
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
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-8px flex-none">
            <FilesSelect v-model="filesStore.filesList" :max="10" />
            <AgentSelect />
          </div>
        </div>
      </template>
    </Sender>
  </div>
</template>

<style scoped lang="scss">
.chat-defaul-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  min-height: 450px;
  
  .chat-defaul-sender {
    justify-self: center;
    width: 80%;
    margin-bottom: 28px;
    padding: 0 24px;
  }
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
</style>
