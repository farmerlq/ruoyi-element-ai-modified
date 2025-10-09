<script setup lang="ts">
import { onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import logoPng from '@/assets/images/logo.png';
import AccountPassword from '@/components/LoginDialog/components/FormLogin/AccountPassword.vue';
import SvgIcon from '@/components/SvgIcon/index.vue';
import { useUserStore } from '@/stores';
import { useLoginFormStore } from '@/stores/modules/loginForm';

const router = useRouter();
const userStore = useUserStore();
const loginFormStore = useLoginFormStore();

const loginFormType = computed(() => loginFormStore.LoginFormType);

// 如果已登录，重定向到首页
onMounted(() => {
  if (userStore.token) {
    router.replace({ name: 'chat' });
  }
});

// 监听登录成功
watch(() => userStore.token, (newToken: string | undefined) => {
  if (newToken) {
    router.replace({ name: 'chat' });
  }
}, { immediate: true });
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="left-section">
        <div class="logo-wrap">
          <img :src="logoPng" class="logo-img">
          <span class="logo-text">Element Plus X</span>
        </div>
        <div class="ad-banner">
          <SvgIcon name="p-bangong" class-name="animate-up-down" />
        </div>
      </div>
      <div class="right-section">
        <div class="content-wrapper">
          <div class="form-box">
            <div v-if="loginFormType === 'AccountPassword'" class="form-container">
              <span class="content-title"> 登录后免费使用完整功能 </span>
              <el-divider content-position="center">
                账号密码登录
              </el-divider>
              <AccountPassword />
            </div>
          </div>
          <div class="footer">
            <p class="copyright">
              © 2024 Element Plus X All Rights Reserved.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 560px;
  background: linear-gradient(150deg, var(--el-color-primary-light-9) 30%, var(--el-color-primary-light-7) 100%);
  background-size: 200% 200%;
  animation: gradientBG 10s ease infinite;

  .login-container {
    display: flex;
    width: 90%;
    height: 80%;
    max-width: 1200px;
    min-height: 600px;
    overflow: hidden;
    background-color: #fff;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);

    .left-section {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 50%;
      height: 100%;
      padding: 40px;
      background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
      color: #fff;

      .logo-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 40px;

        .logo-img {
          width: 80px;
          height: 80px;
          margin-bottom: 20px;
        }

        .logo-text {
          font-size: 24px;
          font-weight: bold;
        }
      }

      .ad-banner {
        font-size: 200px;
        opacity: 0.8;
      }
    }

    .right-section {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 50%;
      height: 100%;
      padding: 40px;

      .content-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;

        .form-box {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          width: 100%;
          height: 100%;
          padding: 20px;

          .form-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            max-width: 360px;

            .content-title {
              margin-bottom: 20px;
              font-size: 24px;
              font-weight: bold;
              text-align: center;
            }
          }
        }

        .footer {
          .copyright {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            text-align: center;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 992px) {
  .login-page {
    .login-container {
      .left-section {
        display: none;
      }

      .right-section {
        width: 100%;
      }
    }
  }
}

@media (max-width: 576px) {
  .login-page {
    .login-container {
      width: 95%;
      height: 90%;

      .right-section {
        padding: 20px;
      }
    }
  }
}

// 背景动画
@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

// 上下浮动动画
@keyframes float {
  0% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-20px);
  }

  100% {
    transform: translateY(0);
  }
}

.animate-up-down {
  animation: float 3s ease-in-out infinite;
}
</style>
