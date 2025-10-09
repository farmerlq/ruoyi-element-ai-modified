import type { Component } from 'vue';

export interface GetSessionListParams {
  /**
   * 创建者
   */
  createBy?: number;
  /**
   * 创建部门
   */
  createDept?: number;
  /**
   * 创建时间
   */
  createTime?: Date;
  /**
   * 主键
   */
  id?: number;
  /**
   * 排序的方向desc或者asc
   */
  isAsc?: string;
  /**
   * 排序列
   */
  orderByColumn?: string;
  /**
   * 当前页数
   */
  pageNum?: number;
  /**
   * 分页大小
   */
  pageSize?: number;
  /**
   * 请求参数
   */
  params?: { [key: string]: { [key: string]: any } };
  /**
   * 备注
   */
  remark?: string;
  /**
   * 会话内容
   */
  sessionContent?: string;
  /**
   * 会话标题
   */
  sessionTitle?: string;
  /**
   * 更新者
   */
  updateBy?: number;
  /**
   * 更新时间
   */
  updateTime?: Date;
  /**
   * 用户id
   */
  userId: number;
}

/**
 * ChatSessionVo，会话管理视图对象 chat_session
 */
export interface ChatSessionVo {
  /**
   * 主键
   */
  // id?: number
  id?: string;
  /**
   * 备注
   */
  remark?: string;
  /**
   * 会话内容
   */
  sessionContent?: string;
  /**
   * 会话标题
   */
  title?: string;
  /**
   * 用户id
   */
  user_id?: number;
  /**
   * 智能体ID
   */
  agent_id?: number;
  /**
   * 商户ID
   */
  merchant_id?: number;
  /**
   * 状态
   */
  status?: string;
  /**
   * 结束时间
   */
  ended_at?: string | null;
  /**
   * 创建时间
   */
  created_at?: string;
  /**
   * 更新时间
   */
  updated_at?: string | null;
  /**
   * 消息条数
   */
  message_count?: number;
  /**
   * 自定义的消息前缀图标字段
   */
  prefixIcon?: Component;
}

/**
 * ChatSessionBo，会话管理业务对象 chat_session
 */
export interface CreateSessionDTO {
  /**
   * 会话标题
   */
  title: string;
  /**
   * 用户id
   */
  user_id: number;
  /**
   * 智能体ID
   */
  agent_id: number;
  /**
   * 商户ID
   */
  merchant_id: number;
  /**
   * 状态
   */
  status: string;
}

// export interface CreateSessionVO {
//   id: number;
// }
