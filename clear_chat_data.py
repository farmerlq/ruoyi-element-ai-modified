#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理聊天数据脚本
用于删除所有对话和消息记录
"""

import os
import sys

# 添加项目根目录和backend目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

try:
    from backend.core.config import settings
    from backend.models.session import Conversation
    from backend.models.message import Message
    from backend.core.database import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

def get_db_session():
    """获取数据库会话"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def clear_chat_data():
    """清理所有聊天数据"""
    db = get_db_session()
    
    try:
        # 统计删除前的数据量
        conversation_count = db.query(Conversation).count()
        message_count = db.query(Message).count()
        
        print(f"删除前数据统计:")
        print(f"  对话数量: {conversation_count}")
        print(f"  消息数量: {message_count}")
        
        # 确认操作
        confirm = input("\n确认要删除所有对话和消息吗? 此操作不可恢复! (输入 'yes' 确认): ")
        if confirm.lower() != 'yes':
            print("操作已取消")
            return
        
        # 删除所有消息
        deleted_messages = db.query(Message).delete()
        print(f"已删除消息数量: {deleted_messages}")
        
        # 删除所有对话
        deleted_conversations = db.query(Conversation).delete()
        print(f"已删除对话数量: {deleted_conversations}")
        
        # 提交事务
        db.commit()
        print("所有聊天数据已成功删除!")
        
    except Exception as e:
        print(f"删除数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

def preview_data():
    """预览将要删除的数据"""
    db = get_db_session()
    
    try:
        # 统计数据量
        conversation_count = db.query(Conversation).count()
        message_count = db.query(Message).count()
        
        print("数据预览:")
        print(f"  对话数量: {conversation_count}")
        print(f"  消息数量: {message_count}")
        
        # 显示最近的几条对话
        print("\n最近的对话:")
        conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).limit(5).all()
        for conv in conversations:
            print(f"  - ID: {conv.id}, 标题: {conv.title}, 更新时间: {conv.updated_at}")
            
        # 显示最近的几条消息
        print("\n最近的消息:")
        messages = db.query(Message).order_by(Message.created_at.desc()).limit(5).all()
        for msg in messages:
            # 处理可能为None的内容
            content_str = str(msg.content) if msg.content is not None else ""
            preview_content = content_str[:50] + "..." if len(content_str) > 50 else content_str
            print(f"  - ID: {msg.id}, 角色: {msg.role}, 内容: {preview_content}")
            
    except Exception as e:
        print(f"预览数据时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='清理聊天数据工具')
    parser.add_argument('--preview', action='store_true', help='预览将要删除的数据')
    
    args = parser.parse_args()
    
    if args.preview:
        preview_data()
    else:
        clear_chat_data()