<!-- 标题编辑 -->
<script setup lang="ts">
import SvgIcon from '@/components/SvgIcon/index.vue';
import { computed } from 'vue';
import { ElMessageBox } from 'element-plus';
import { useSessionStore } from '@/stores/modules/session';

const sessionStore = useSessionStore();

const currentSession = computed(() => sessionStore.currentSession);

function handleClickTitle() {
  ElMessageBox.prompt('', '编辑对话名称', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputErrorMessage: '请输入对话名称',
    confirmButtonClass: 'el-button--primary',
    cancelButtonClass: 'el-button--info',
    roundButton: true,
    inputValue: currentSession.value?.title,
    inputValidator: (value) => {
      if (!value) {
        return false;
      }
      return true;
    },
  })
    .then(({ value }) => {
      sessionStore
        .updateSession({
          id: currentSession.value!.id,
          title: value,
          sessionContent: currentSession.value!.sessionContent,
        })
        .then(() => {
          ElMessage({
            type: 'success',
            message: '修改成功',
          });
          nextTick(() => {
            // 如果是当前会话，则更新当前选中会话信息
            sessionStore.setCurrentSession({
              ...currentSession.value,
              title: value,
            });
          });
        });
    })
    .catch(() => {
      // ElMessage({
      //   type: 'info',
      //   message: '取消修改',
      // });
    });
}
</script>

<template>
  <div v-if="currentSession" class="title-container">
    <div class="title-wrapper">
      <div
        class="title-editing-container"
        @click="handleClickTitle"
      >
        <div class="title-text">
          {{ currentSession?.title }}
        </div>
        <SvgIcon name="draft-line" class="edit-icon" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.title-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.title-wrapper {
  box-sizing: border-box;
  margin-right: 20px;
}

.title-editing-container {
  padding: 4px;
  width: fit-content;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  cursor: pointer;
  select: none;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.title-editing-container:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.title-text {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  select: none;
  padding-right: 8px;
}

.edit-icon {
  flex-shrink: 0;
  color: #999;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.title-editing-container:hover .edit-icon {
  display: block;
  opacity: 1;
}

@media (max-width: 768px) {
  .title-text {
    font-size: 18px;
  }
  
  .title-wrapper {
    margin-right: 12px;
  }
}
</style>