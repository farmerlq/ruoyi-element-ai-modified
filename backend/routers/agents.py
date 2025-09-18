from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.deps import get_current_user_or_raise
from core.security import get_current_merchant_id
from models.agent import Agent
from schemas.agent import AgentCreate, AgentUpdate, Agent as AgentSchema
import json

router = APIRouter()

@router.post("/", response_model=AgentSchema, status_code=201)
def create_agent(
    agent: AgentCreate,
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id),
    db: Session = Depends(get_db)
):
    # 确保当前用户有权限创建智能体
    if merchant_id and agent.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # 确保config是字典格式
    agent_dict = agent.dict()
    if isinstance(agent_dict.get('config'), str):
        try:
            agent_dict['config'] = json.loads(agent_dict['config'])
        except:
            agent_dict['config'] = {}
    
    db_agent = Agent(**agent_dict)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/{agent_id}", response_model=AgentSchema)
def read_agent(
    agent_id: int,
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id),
    db: Session = Depends(get_db)
):
    db_agent = db.query(Agent).filter(Agent.id == agent_id)
    
    # 如果有商户ID，添加商户过滤
    if merchant_id:
        db_agent = db_agent.filter(Agent.merchant_id == merchant_id)
        
    db_agent = db_agent.first()
    
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.get("/", response_model=List[AgentSchema])
def read_agents(
    skip: int = 0, 
    limit: int = 100,
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id),
    db: Session = Depends(get_db)
):
    query = db.query(Agent)
    
    # 如果有商户ID，添加商户过滤
    if merchant_id:
        query = query.filter(Agent.merchant_id == merchant_id)
        
    agents = query.offset(skip).limit(limit).all()
    
    # 处理可能的配置字段问题
    for agent in agents:
        if isinstance(agent.config, str):
            try:
                agent.config = json.loads(agent.config)
            except:
                agent.config = {}
    return agents

@router.put("/{agent_id}", response_model=AgentSchema)
def update_agent(
    agent_id: int, 
    agent: AgentUpdate,
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id),
    db: Session = Depends(get_db)
):
    db_agent = db.query(Agent).filter(Agent.id == agent_id)
    
    # 如果有商户ID，添加商户过滤
    if merchant_id:
        db_agent = db_agent.filter(Agent.merchant_id == merchant_id)
        
    db_agent = db_agent.first()
    
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 检查是否有权限更新
    if merchant_id and db_agent.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    update_data = agent.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'config' and isinstance(value, str):
            try:
                value = json.loads(value)
            except:
                pass
        setattr(db_agent, key, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.delete("/{agent_id}", status_code=204)
def delete_agent(
    agent_id: int,
    current_user = Depends(get_current_user_or_raise),
    merchant_id: int = Depends(get_current_merchant_id),
    db: Session = Depends(get_db)
):
    db_agent = db.query(Agent).filter(Agent.id == agent_id)
    
    # 如果有商户ID，添加商户过滤
    if merchant_id:
        db_agent = db_agent.filter(Agent.merchant_id == merchant_id)
        
    db_agent = db_agent.first()
    
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 检查是否有权限删除
    if merchant_id and db_agent.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    db.delete(db_agent)
    db.commit()
    return