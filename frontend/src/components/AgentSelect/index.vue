<!-- 切换智能体 -->
<script setup lang="ts">
import type { AgentVO } from '@/api/agent/types';
import Popover from '@/components/Popover/index.vue';
import SvgIcon from '@/components/SvgIcon/index.vue';
import { useAgentStore } from '@/stores/modules/agent';
import { computed, ref, onMounted } from 'vue';

const agentStore = useAgentStore();

onMounted(async () => {
  await agentStore.requestAgentList();
  // 设置默认智能体
  if (
    agentStore.agentList.length > 0
    && (!agentStore.currentAgentInfo || !agentStore.currentAgentInfo.name)
  ) {
    agentStore.setCurrentAgentInfo(agentStore.agentList[0]);
  }
});

const currentAgentName = computed(
  () => agentStore.currentAgentInfo && agentStore.currentAgentInfo.name,
);
const popoverList = computed(() => agentStore.agentList);

/* 弹出面板 开始 */
const popoverStyle = ref({
  width: '200px',
  padding: '4px',
  height: 'fit-content',
  background: 'var(--el-bg-color, #fff)',
  border: '1px solid var(--el-border-color-light)',
  borderRadius: '8px',
  boxShadow: '0 2px 12px 0 rgba(0, 0, 0, 0.1)',
});
const popoverRef = ref();

// 显示
async function showPopover() {
  // 获取最新的智能体列表
  await agentStore.requestAgentList();
}

// 点击
function handleClick(item: AgentVO) {
  agentStore.setCurrentAgentInfo(item);
  popoverRef.value?.hide?.();
}
</script>

<template>
  <div class="agent-select">
    <Popover
      ref="popoverRef"
      placement="bottom-start"
      :offset="[4, 4]"
      popover-class="popover-content"
      :popover-style="popoverStyle"
      trigger="click"
      @show="showPopover"
    >
      <!-- 触发元素插槽 -->
      <template #trigger>
        <div
          class="agent-select-box select-none flex items-center gap-4px p-10px rounded-10px cursor-pointer font-size-12px border-1px border-[rgba(0,0,0,0.08)] border-solid"
        >
          <div class="agent-select-box-icon">
            <SvgIcon name="models" size="12" />
          </div>
          <div class="agent-select-box-text font-size-12px">
            {{ currentAgentName }}
          </div>
        </div>
      </template>

      <div class="popover-content-box">
        <div
          v-for="item in popoverList"
          :key="item.id"
          class="popover-content-box-items w-full rounded-8px select-none transition-all transition-duration-300 flex items-center hover:cursor-pointer hover:bg-[rgba(0,0,0,.04)]"
        >
          <Popover
            trigger-class="popover-trigger-item-text"
            popover-class="rounded-tooltip"
            placement="right"
            trigger="hover"
            :offset="[12, 0]"
          >
            <template #trigger>
              <div
                class="popover-content-box-item p-4px font-size-12px text-overflow line-height-16px"
                :class="{ 'bg-[rgba(0,0,0,.04)] is-select': item.name === currentAgentName }"
                @click="handleClick(item)"
              >
                {{ item.name }}
              </div>
            </template>
            <div
              class="popover-content-box-item-text text-wrap max-w-200px rounded-lg p-8px font-size-12px line-height-tight"
            >
              {{ item.description }}
            </div>
          </Popover>
        </div>
      </div>
    </Popover>
  </div>
</template>

<style scoped lang="scss">
.agent-select-box {
  color: var(--el-color-primary, #409eff);
  background: var(--el-color-primary-light-9, rgb(235.9 245.3 255));
  border: 1px solid var(--el-color-primary, #409eff);
  border-radius: 10px;
}

// 为智能体列表添加更高的z-index，确保不被消息内容遮挡
.popover-content {
  z-index: 1001 !important;
}
.popover-content-box-item.is-select {
  font-weight: 700;
  color: var(--el-color-primary, #409eff);
}
.popover-content-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  height: 200px;
  overflow: hidden auto;
  .popover-content-box-items {
    :deep(.popover-trigger-item-text) {
      width: 100%;
    }
  }
  .popover-content-box-item-text {
    color: white;
    background-color: black;
  }

  // 滚动条样式
  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-track {
    background: #f5f5f5;
  }
  &::-webkit-scrollbar-thumb {
    background: #cccccc;
    border-radius: 4px;
  }
}
</style>
