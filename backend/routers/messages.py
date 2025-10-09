from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
from core.database import get_db
from core.deps import get_optional_current_user
from models.message import Message as DBMessage
from models.session import Conversation
from schemas.message import MessageCreate, MessageUpdate, Message as MessageSchema

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=MessageSchema, status_code=201)
def create_message(
    message: MessageCreate, 
    db: Session = Depends(get_db)
):
    try:
        db_message = DBMessage(**message.dict())
        db.add(db_message)
        
        # 更新会话的更新时间
        if message.conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
            if conversation:
                # SQLAlchemy会自动处理onupdate，不需要手动设置updated_at
                # 只需要触发SQLAlchemy的更新机制
                conversation.title = conversation.title  # 触发更新
        
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[MessageSchema])
def read_messages(
    skip: int = 0, 
    limit: int = 100, 
    session_id: Optional[str] = None,  # 保持向后兼容
    conversation_id: Optional[str] = None,  # 添加新的参数名
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)  # 改为可选用户依赖
):
    try:
        # 优先使用 conversation_id，如果没有则使用 session_id
        filter_id = conversation_id if conversation_id is not None else session_id
        query = db.query(DBMessage)
        
        # 添加会话ID过滤（使用conversation_id字段）
        if filter_id:
            query = query.filter(DBMessage.conversation_id == filter_id)
            
        messages = query.offset(skip).limit(limit).all()
        
        # 检查第一条消息的序列化
        if messages:
            # 尝试序列化第一条消息来检查错误
            try:
                MessageSchema.model_validate(messages[0])
            except Exception as e:
                logger.error(f"Serialization failed for message {messages[0].id}: {str(e)}", exc_info=True)
                raise
        
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{message_id}", response_model=MessageSchema)
def read_message(
    message_id: int, 
    db: Session = Depends(get_db)
):
    try:
        db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
        
        if db_message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        return db_message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{message_id}", response_model=MessageSchema)
def update_message(
    message_id: int, 
    message: MessageUpdate, 
    db: Session = Depends(get_db)
):
    try:
        db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
        
        if db_message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        
        for key, value in message.dict(exclude_unset=True).items():
            setattr(db_message, key, value)
            
        db.commit()
        db.refresh(db_message)
        return db_message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/all", status_code=204)
def delete_all_messages(
    db: Session = Depends(get_db)
):
    try:
        # 删除所有消息
        db.query(DBMessage).delete()
        db.commit()
        return
    except Exception as e:
        logger.error(f"Error deleting all messages: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int, 
    db: Session = Depends(get_db)
):
    try:
        db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
        
        if db_message is None:
            raise HTTPException(status_code=404, detail="Message not found")
            
        db.delete(db_message)
        db.commit()
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")