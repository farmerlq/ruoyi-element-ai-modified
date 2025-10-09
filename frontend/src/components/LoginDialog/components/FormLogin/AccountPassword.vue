<!-- 账号密码登录表单 -->
<script lang="ts" setup>
import type { FormInstance, FormRules } from 'element-plus';
import type { LoginDTO } from '@/api/auth/types';
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '@/api';
import { useUserStore } from '@/stores';
import { useSessionStore } from '@/stores/modules/session';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const sessionStore = useSessionStore();

const formRef = ref<FormInstance>();

const formModel = reactive<LoginDTO>({
  username: '',
  password: '',
});

const rules = reactive<FormRules<LoginDTO>>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
});

const router = useRouter();
const loading = ref(false);

async function handleSubmit() {
  try {
    loading.value = true;
    await formRef.value?.validate();
    const res = await login(formModel);

    // 检查响应数据结构并提取token
    const token = res.data?.access_token || res.data?.token;

    if (token) {
      userStore.setToken(token);
    }
    else {
      ElMessage.error('登录失败，未返回有效token');
      return;
    }

    if (res.data.userInfo) {
      // 后端已直接返回user_id字段，无需额外映射
      userStore.setUserInfo(res.data.userInfo);
    }

    ElMessage.success('登录成功');
    userStore.closeLoginDialog();
    // 立刻获取回话列表
    await sessionStore.requestSessionList(1, true);
    router.replace('/');
  }
  catch (error: any) {
    // 根据错误类型显示不同的错误信息
    if (error?.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    }
    else if (error?.message) {
      ElMessage.error(error.message);
    }
    else {
      ElMessage.error('登录失败，请稍后重试');
    }
  }
  finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="custom-form">
    <el-form
      ref="formRef"
      :model="formModel"
      :rules="rules"
      style="width: 230px"
      @submit.prevent="handleSubmit"
    >
      <el-form-item prop="username">
        <el-input v-model="formModel.username" placeholder="请输入用户名">
          <template #prefix>
            <el-icon>
              <User />
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="formModel.password"
          placeholder="请输入密码"
          type="password"
          show-password
        >
          <template #prefix>
            <el-icon>
              <Lock />
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          style="width: 100%"
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
