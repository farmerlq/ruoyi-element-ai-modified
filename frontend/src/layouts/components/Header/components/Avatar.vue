<!-- 头像 -->
<script setup lang="ts">
import { ArrowDown } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox, ElPopover } from 'element-plus';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import SvgIcon from '@/components/SvgIcon/index.vue';
import { useUserStore } from '@/stores';
import { useSessionStore } from '@/stores/modules/session';

const userStore = useUserStore();
const sessionStore = useSessionStore();
const router = useRouter();
const src = computed(
  () => userStore.userInfo?.avatar ?? 'https://avatars.githubusercontent.com/u/76239030',
);

/* 弹出面板 开始 */
const popoverRef = ref();

// 弹出面板内容
const popoverList = ref([
  {
    key: '1',
    title: '我的账号',
    icon: 'user-fill',
  },
  {
    key: '2',
    title: '系统设置',
    icon: 'settings-4-fill',
  },
  {
    key: '3',
    divider: true,
  },
  {
    key: '4',
    title: '退出登录',
    icon: 'logout-box-r-line',
  },
]);

// 点击
function handleClick(item: any) {
  switch (item.key) {
    case '1':
      ElMessage.warning('暂未开放');
      break;
    case '2':
      ElMessage.warning('暂未开放');
      break;
    case '4':
      popoverRef.value?.hide?.();
      ElMessageBox.confirm('退出登录不会丢失任何数据，你仍可以登录此账号。', '确认退出登录？', {
        confirmButtonText: '确认退出',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        cancelButtonClass: 'el-button--info',
        roundButton: true,
        autofocus: false,
      })
        .then(async () => {
          // 在这里执行退出方法
          await userStore.logout();
          // 清空回话列表
          await sessionStore.requestSessionList(1, true);
          await sessionStore.createSessionBtn();
          // 直接跳转到登录页面
          router.push('/login');
        })
        .catch(() => {
          // ElMessage({
          //   type: 'info',
          //   message: '取消',
          // });
        });
      break;
    default:
      break;
  }
}

/* 弹出面板 结束 */
</script>

<template>
  <div class="avatar-container">
    <ElPopover
      ref="popoverRef"
      placement="top-start"
      trigger="click"
      popper-class="user-popover"
      :width="200"
    >
      <!-- 弹出内容 -->
      <div class="popover-content-box shadow-lg">
        <div v-for="item in popoverList" :key="item.key" class="popover-content-box-items h-full">
          <div
            v-if="!item.divider"
            class="popover-content-box-item flex items-center h-full gap-8px p-8px pl-10px pr-12px rounded-lg hover:cursor-pointer hover:bg-[rgba(0,0,0,.04)]"
            @click="handleClick(item)"
          >
            <SvgIcon :name="item.icon!" size="16" class-name="flex-none" />
            <div class="popover-content-box-item-text font-size-14px text-overflow max-h-120px">
              {{ item.title }}
            </div>
          </div>

          <div v-if="item.divider" class="divder h-1px bg-gray-200 my-4px" />
        </div>
      </div>

      <!-- 触发元素 -->
      <template #reference>
        <div class="user-trigger flex items-center gap-8px p-8px rounded-lg hover:bg-[rgba(0,0,0,.04)]" style="cursor: pointer;">
          <el-avatar :src="src" :size="28" fit="fit" shape="circle" />
          <div class="user-details flex-1 min-w-0">
            <div class="user-name font-size-14px font-500 text-overflow">
              {{ userStore.userInfo?.nickName || userStore.userInfo?.username || '用户' }}
            </div>
            <div class="user-email font-size-12px text-overflow" style="color: rgb(0 0 0 / 60%)">
              {{ userStore.userInfo?.username }}
            </div>
          </div>
          <el-icon>
            <ArrowDown />
          </el-icon>
        </div>
      </template>
    </ElPopover>
  </div>
</template>

<style scoped lang="scss">
.user-popover {
  z-index: 1001 !important;
}
.popover-content-box {
  padding: 8px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgb(0 0 0 / 8%);
}
</style>
