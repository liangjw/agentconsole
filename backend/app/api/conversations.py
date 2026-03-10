from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app import models, schemas

router = APIRouter()

@router.post("", response_model=schemas.Conversation)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db)
):
    # 获取代理配置
    agent = db.query(models.Agent).filter(models.Agent.id == conversation.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 创建沙箱
    sandbox_id = f"sandbox_{agent.id}_{id(conversation)}"

    # 创建会话
    db_conversation = models.Conversation(
        agent_id=conversation.agent_id,
        user_id=conversation.user_id,
        sandbox_id=sandbox_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation

@router.get("/{conversation_id}", response_model=schemas.Conversation)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.get("/{conversation_id}/messages", response_model=List[schemas.Message])
def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.created_at).all()
    return messages

@router.post("/{conversation_id}/messages", response_model=schemas.Message)
async def send_message(
    conversation_id: str,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db)
):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 保存用户消息
    db_message = models.Message(
        conversation_id=conversation_id,
        role="user",
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # 获取代理配置
    agent = db.query(models.Agent).filter(
        models.Agent.id == conversation.agent_id
    ).first()

    # 获取历史消息用于上下文
    history = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.created_at).all()

    # 构建代理响应 (简化版: 实际应该调用AI)
    response_content = f"我理解了您的请求: {message.content}\n\n"
    response_content += "这是一个模拟响应。在实际实现中，这里会调用AI模型来分析请求，"
    response_content += "根据配置的Skills在沙箱中执行相应的操作，并返回结果。"

    # 保存代理响应
    db_response = models.Message(
        conversation_id=conversation_id,
        role="assistant",
        content=response_content
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    return db_response

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 删除会话
    db.delete(conversation)
    db.commit()

    return {"message": "Conversation ended"}
