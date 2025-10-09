import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';
import { useNProgress } from '@vueuse/integrations/useNProgress';
import { createRouter, createWebHistory } from 'vue-router';
import { ROUTER_WHITE_LIST } from '@/config';
import { errorRouter, layoutRouter, staticRouter } from '@/routers/modules/staticRouter';
import { useUserStore } from '@/stores';

const { start, done } = useNProgress(0, {
  showSpinner: false,
  trickleSpeed: 200,
  minimum: 0.3,
  easing: 'ease',
  speed: 500,
});

const router = createRouter({
  history: createWebHistory(),
  routes: [...layoutRouter, ...staticRouter, ...errorRouter],
  strict: false,
  scrollBehavior: () => ({ left: 0, top: 0 }),
});

// 路由前置守卫
router.beforeEach(
  async (
    to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext,
  ) => {
    const userStore = useUserStore();

    // 启动进度条
    start();

    // 设置页面标题
    document.title = (to.meta.title as string) || (import.meta.env.VITE_WEB_TITLE as string);

    // 白名单路由直接放行
    if (ROUTER_WHITE_LIST.includes(to.path)) {
      return next();
    }

    // 无 Token 时强制跳转登录页
    if (!userStore.token) {
      return next({ name: 'login' });
    }

    // 正常访问页面
    next();
  },
);

// 路由跳转错误
router.onError((error) => {
  // 结束全屏动画
  done();
  // 路由错误处理
});

// 后置路由
router.afterEach(() => {
  // 结束全屏动画
  done();
});

export default router;