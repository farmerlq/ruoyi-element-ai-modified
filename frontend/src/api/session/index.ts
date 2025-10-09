import type {
  ChatSessionVo,
  CreateSessionDTO,
  // CreateSessionVO,
  GetSessionListParams,
} from './types';
import { del, get, post, put } from '@/utils/request';

export function get_session_list(params: GetSessionListParams) {
  return get<ChatSessionVo[]>('/sessions/', {
    params: {
      user_id: params.userId,
      page: params.pageNum,
      size: params.pageSize,
    },
  });
}

export function create_session(data: CreateSessionDTO) {
  const requestData = {
    title: data.title,
    user_id: data.user_id,
    agent_id: data.agent_id,
    merchant_id: data.merchant_id,
    status: data.status,
  };
  return post<ChatSessionVo>('/sessions/', requestData);
}

export function update_session(data: ChatSessionVo) {
  const requestData = {
    id: data.id, // 添加必需的id字段
    title: data.title,
    user_id: data.user_id,
    agent_id: data.agent_id,
    merchant_id: data.merchant_id,
  };
  return put(`/sessions/${data.id}`, requestData);
}

export function get_session(id: string) {
  return get<ChatSessionVo>(`/sessions/${id}`);
}

export function delete_session(ids: string[]) {
  // 后端API需要逐个删除
  const promises = ids.map(id => del(`/sessions/${id}`));
  return Promise.all(promises);
}
