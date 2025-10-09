import type { EmailCodeDTO, LoginDTO, LoginVO } from './types';
import { post } from '@/utils/request';

export const login = (data: LoginDTO) => post<LoginVO>('/auth/login', data);

// 邮箱验证码
export const emailCode = (data: EmailCodeDTO) => post('/auth/email/code', data);
