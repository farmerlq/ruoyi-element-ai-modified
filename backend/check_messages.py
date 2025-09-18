import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from core.database import SessionLocal
from models.message import Message

def check_messages():
    db = SessionLocal()
    try:
        messages = db.query(Message).order_by(Message.id.desc()).limit(5).all()
        print('Latest messages:')
        for msg in messages:
            print(f'ID: {msg.id}, Content: {msg.content[:50]}, Workflow Events: {msg.workflow_events}')
    finally:
        db.close()

if __name__ == "__main__":
    check_messages()