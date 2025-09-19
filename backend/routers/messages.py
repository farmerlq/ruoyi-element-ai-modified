from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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
        logger.debug(f"Creating message: {message}")
        db_message = DBMessage(**message.dict())
        db.add(db_message)
        
        # 更新会话的更新时间
        if message.conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_message)
        logger.debug(f"Message created successfully: {db_message.id}")
        return db_message
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{message_id}", response_model=MessageSchema)
def read_message(
    message_id: int, 
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Fetching message with id: {message_id}")
        db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
        
        if db_message is None:
            logger.debug(f"Message with id {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")
        logger.debug(f"Message found: {db_message.id}")
        return db_message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[MessageSchema])
def read_messages(
    skip: int = 0, 
    limit: int = 100, 
    session_id: str = None,  # 保持向后兼容
    conversation_id: str = None,  # 添加新的参数名
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)  # 改为可选用户依赖
):
    try:
        # 优先使用 conversation_id，如果没有则使用 session_id
        filter_id = conversation_id if conversation_id is not None else session_id
        logger.debug(f"Fetching messages with filter_id: {filter_id}, skip: {skip}, limit: {limit}")
        query = db.query(DBMessage)
        
        # 添加会话ID过滤（使用conversation_id字段）
        if filter_id:
            query = query.filter(DBMessage.conversation_id == filter_id)
            
        messages = query.offset(skip).limit(limit).all()
        logger.debug(f"Found {len(messages)} messages")
        
        # 调试：检查第一条消息的序列化
        if messages:
            logger.debug(f"First message id: {messages[0].id}, content length: {len(messages[0].content) if messages[0].content else 0}")
            # 尝试序列化第一条消息来检查错误
            try:
                message_data = MessageSchema.model_validate(messages[0])
                logger.debug(f"Serialization successful for message {messages[0].id}")
            except Exception as e:
                logger.error(f"Serialization failed for message {messages[0].id}: {str(e)}", exc_info=True)
                raise
        
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{message_id}", response_model=MessageSchema)
def update_message(
    message_id: int, 
    message: MessageUpdate, 
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Updating message with id: {message_id}")
        db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
        
        if db_message is None:
            logger.debug(f"Message with id {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")
        
        for key, value in message.dict(exclude_unset=True).items():
            setattr(db_message, key, value)
            
        db.commit()
        db.refresh(db_message)
        logger.debug(f"Message updated successfully: {db_message.id}")
        return db_message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int, 
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Deleting message with id: {message_id}")
        db_message = db.query(DBMessage).filter(DBMessage.id == message_id).first()
        
        if db_message is None:
            logger.debug(f"Message with id {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")
            
        db.delete(db_message)
        db.commit()
        logger.debug(f"Message deleted successfully: {message_id}")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")