#!/usr/bin/env python3
"""
清理历史消息中错误的workflow_events数据
移除text_chunk和message事件，只保留真正的工作流事件
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.message import Message
from typing import List, Dict, Any, Union, cast

def clean_workflow_events():
    """清理workflow_events中的错误事件"""
    db = SessionLocal()
    try:
        # 获取所有包含workflow_events的消息
        messages = db.query(Message).filter(Message.workflow_events.isnot(None)).all()
        
        cleaned_count = 0
        total_messages = len(messages)
        
        print(f"找到 {total_messages} 条包含workflow_events的消息")
        
        for message in messages:
            # 确保 workflow_events 是列表类型
            workflow_events = message.workflow_events
            if workflow_events is None or not isinstance(workflow_events, list):
                continue
                
            original_count = len(workflow_events)
            
            # 过滤掉text_chunk和message事件
            filtered_events: List[Dict[str, Any]] = []
            for event in workflow_events:
                if isinstance(event, dict):
                    event_type = event.get('event', '')
                    # 只保留真正的工作流相关事件
                    if event_type and ('workflow' in event_type or 'node' in event_type):
                        filtered_events.append(event)
            
            # 如果事件数量有变化，更新数据库
            if len(filtered_events) != original_count:
                # 正确地将修改后的列表赋值给字段
                message.workflow_events = filtered_events if filtered_events else None
                cleaned_count += 1
                
                if len(filtered_events) == 0:
                    print(f"消息 {message.id}: 移除了所有 {original_count} 个事件")
                else:
                    print(f"消息 {message.id}: 从 {original_count} 个事件过滤到 {len(filtered_events)} 个事件")
        
        if cleaned_count > 0:
            db.commit()
            print(f"\n成功清理了 {cleaned_count} 条消息的workflow_events数据")
        else:
            print("没有需要清理的数据")
            
    except Exception as e:
        db.rollback()
        print(f"清理过程中发生错误: {e}")
        raise
    finally:
        db.close()

def preview_cleanup():
    """预览将要清理的数据"""
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(Message.workflow_events.isnot(None)).all()
        
        print("=== 预览清理数据 ===")
        print(f"找到 {len(messages)} 条包含workflow_events的消息")
        
        for message in messages[:5]:  # 只预览前5条
            # 确保 workflow_events 是列表类型
            workflow_events = message.workflow_events
            if workflow_events is not None and isinstance(workflow_events, list) and workflow_events:
                print(f"\n消息 ID: {message.id}")
                print(f"事件数量: {len(workflow_events)}")
                for i, event in enumerate(workflow_events[:3]):  # 只显示前3个事件
                    if isinstance(event, dict):
                        event_type = event.get('event', '未知')
                        print(f"  事件 {i+1}: {event_type}")
                if len(workflow_events) > 3:
                    print(f"  ... 还有 {len(workflow_events) - 3} 个事件")
        
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='清理workflow_events中的错误事件')
    parser.add_argument('--preview', action='store_true', help='只预览数据，不实际执行清理')
    
    args = parser.parse_args()
    
    if args.preview:
        preview_cleanup()
    else:
        print("开始清理workflow_events数据...")
        clean_workflow_events()
        print("清理完成！")