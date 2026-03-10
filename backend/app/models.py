from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
import uuid
from datetime import datetime
from backend.app.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, default="")
    skills = Column(JSON, default=list)
    image = Column(String, default="python:3.11")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"))
    user_id = Column(String, default="default_user")
    sandbox_id = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    tool_calls = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
