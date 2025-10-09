import type { ChatMessageVo, GetChatListParams, SendDTO } from './types';
import { get, post } from '@/utils/request';

// 发送消息
export const send = (data: SendDTO) => post<null>('/chat/completions', data);

// 新增对应会话聊天记录
export function addChat(data: ChatMessageVo) {
  return post('/messages/', data);
}

// 获取当前会话的聊天记录
export function getChatList(params: GetChatListParams) {
  return get<ChatMessageVo[]>('/messages/', {
    params: {
      conversation_id: params.sessionId,
    },
  });
}
