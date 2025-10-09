// ConversationItem 类型定义
export interface ConversationItem {
  id: string;
  title: string;
  type: string;
  isActive?: boolean;
  createTime?: string;
  updateTime?: string;
  avatar?: string;
  unreadCount?: number;
  // 可以根据实际业务需求添加更多字段
}

// 定义菜单命令类型
export type ConversationMenuCommand = 'delete' | 'rename' | number;