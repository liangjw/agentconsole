from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    description: str = ""
    skills: List[str] = []
    image: str = "python:3.11"

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    pass

class Agent(AgentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class Message(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    tool_calls: List[Any] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    agent_id: str
    user_id: str = "default_user"

class Conversation(BaseModel):
    id: str
    agent_id: str
    user_id: str
    sandbox_id: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class Skill(BaseModel):
    id: str
    name: str
    description: str
    type: str
    definition: dict
    icon: str = "🔧"

class AgentTemplate(BaseModel):
    id: str
    name: str
    description: str
    skills: List[str]
    image: str
    icon: str = "🤖"
    category: str = "通用"
