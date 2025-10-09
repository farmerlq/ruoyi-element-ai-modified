import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import axios from 'axios';
import { useUserStore } from '@/stores/modules/user';

// 从环境变量获取API基础URL，如果没有设置则使用默认值
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 创建一个包装器，添加.json()方法以兼容fetch API风格
interface WrappedAxiosResponse<T> extends AxiosResponse<T> {
  json: () => Promise<T>;
}

// 创建包装函数确保响应对象有 json 方法
function wrapResponse<T>(response: AxiosResponse<T>): WrappedAxiosResponse<T> {
  // 创建一个包含所有原始响应属性的新对象
  const wrappedResponse = {
    ...response,
    json: () => Promise.resolve(response.data),
  } as WrappedAxiosResponse<T>;

  return wrappedResponse;
}

class Request {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token
        const userStore = useUserStore();
        if (userStore.token) {
          config.headers.Authorization = `Bearer ${userStore.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      },
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // 添加.json()方法以兼容fetch API风格
        return wrapResponse(response);
      },
      (error) => {
        // 处理401未授权错误
        if (error.response?.status === 401) {
          const userStore = useUserStore();
          userStore.clearToken();
          userStore.clearUserInfo();
          // 跳转到登录页
          if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      },
    );
  }

  public get<T>(url: string, config?: AxiosRequestConfig): Promise<WrappedAxiosResponse<T>> {
    return this.instance.get<T>(url, config).then(wrapResponse);
  }

  public post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<WrappedAxiosResponse<T>> {
    return this.instance.post<T>(url, data, config).then(wrapResponse);
  }

  public put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<WrappedAxiosResponse<T>> {
    return this.instance.put<T>(url, data, config).then(wrapResponse);
  }

  public delete<T>(url: string, config?: AxiosRequestConfig): Promise<WrappedAxiosResponse<T>> {
    return this.instance.delete<T>(url, config).then(wrapResponse);
  }

  public patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<WrappedAxiosResponse<T>> {
    return this.instance.patch<T>(url, data, config).then(wrapResponse);
  }
}

const requestInstance = new Request();
export const request = requestInstance;
export const get = requestInstance.get.bind(requestInstance);
export const post = requestInstance.post.bind(requestInstance);
export const put = requestInstance.put.bind(requestInstance);
export const del = requestInstance.delete.bind(requestInstance);
export const patch = requestInstance.patch.bind(requestInstance);
