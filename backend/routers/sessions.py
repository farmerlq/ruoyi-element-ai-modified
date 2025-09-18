from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import List
from core.database import get_db
from core.deps import get_current_user_or_raise
from core.security import get_current_merchant_id
from models.session import Conversation
from models.message import Message
from schemas.session import ConversationCreate, ConversationUpdate, Conversation as ConversationSchema

router = APIRouter()

import uuid

@router.post("/", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: ConversationCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id)
):
    # 检查权限
    if merchant_id and conversation.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # 生成UUID作为会话ID
    conversation_data = conversation.dict()
    conversation_data["id"] = str(uuid.uuid4())
    
    db_conversation = Conversation(**conversation_data)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.get("/{conversation_id}", response_model=ConversationSchema)
def read_conversation(
    conversation_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id)
):
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id)
    
    # 添加商户过滤
    if merchant_id:
        db_conversation = db_conversation.filter(Conversation.merchant_id == merchant_id)
        
    db_conversation = db_conversation.first()
    
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation

@router.get("/", response_model=List[ConversationSchema])
def read_conversations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id)
):
    query = db.query(Conversation)
    
    # 添加商户过滤
    if merchant_id:
        query = query.filter(Conversation.merchant_id == merchant_id)
        
    conversations = query.offset(skip).limit(limit).all()
    
    # 为每个会话查询消息条数
    for conversation in conversations:
        message_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conversation.id
        ).scalar()
        # 将消息条数添加到会话对象中
        conversation.message_count = message_count
    
    return conversations

@router.put("/{conversation_id}", response_model=ConversationSchema)
def update_conversation(
    conversation_id: str, 
    conversation: ConversationUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id)
):
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id)
    
    # 添加商户过滤
    if merchant_id:
        db_conversation = db_conversation.filter(Conversation.merchant_id == merchant_id)
        
    db_conversation = db_conversation.first()
    
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 检查权限
    if merchant_id and db_conversation.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    for key, value in conversation.dict(exclude_unset=True).items():
        setattr(db_conversation, key, value)
        
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id)
):
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id)
    
    # 添加商户过滤
    if merchant_id:
        db_conversation = db_conversation.filter(Conversation.merchant_id == merchant_id)
        
    db_conversation = db_conversation.first()
    
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 检查权限
    if merchant_id and db_conversation.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db.delete(db_conversation)
    db.commit()
    return None