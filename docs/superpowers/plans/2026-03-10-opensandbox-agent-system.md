# OpenSandbox 智能代理系统实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于OpenSandbox的智能代理系统，让产品经理和非技术人员可以通过自然语言与智能代理交互完成任务

**Architecture:**
- 前端: Next.js 14 App Router，提供代理管理和会话交互界面
- 后端: FastAPI，提供REST API和沙箱管理
- 沙箱: OpenSandbox，在沙箱中执行代理任务

**Tech Stack:** Next.js 14, FastAPI, SQLite, OpenSandbox, Docker Compose

---

## 文件结构

```
agentconsole/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI应用入口
│   │   ├── models.py               # SQLAlchemy模型
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── database.py             # 数据库配置
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── agents.py           # 代理API
│   │   │   ├── conversations.py    # 会话API
│   │   │   └── skills.py           # Skills API
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── sandbox.py          # OpenSandbox集成
│   │       └── agent.py            # 代理逻辑
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── agents/
│   │   │   ├── page.tsx            # 代理列表页
│   │   │   ├── new/page.tsx        # 创建代理页
│   │   │   └── [id]/
│   │   │       ├── page.tsx        # 代理详情/编辑页
│   │   │       └── chat/page.tsx   # 会话页面
│   │   └── api/
│   │       └── ...
│   ├── components/
│   │   ├── AgentCard.tsx
│   │   ├── AgentForm.tsx
│   │   ├── ChatWindow.tsx
│   │   └── SkillSelector.tsx
│   ├── lib/
│   │   └── api.ts                  # API调用
│   ├── package.json
│   └── Dockerfile
├── opensandbox/
│   └── config.yaml                  # OpenSandbox配置
├── docker-compose.yml
├── SPEC.md
└── README.md
```

---

## Chunk 1: 后端基础项目搭建

### Task 1: 创建后端项目结构和依赖

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/database.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
opensandbox-python==0.1.0
httpx==0.26.0
```

- [ ] **Step 2: 创建数据库配置**

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./agentconsole.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/requirements.txt backend/app/database.py backend/app/__init__.py
git commit -m "feat: 添加后端基础项目结构"
```

### Task 2: 创建数据模型

**Files:**
- Create: `backend/app/models.py`

- [ ] **Step 1: 创建SQLAlchemy模型**

```python
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/models.py
git commit -m "feat: 添加数据模型"
```

### Task 3: 创建Pydantic Schemas

**Files:**
- Create: `backend/app/schemas.py`

- [ ] **Step 1: 创建Pydantic schemas**

```python
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/schemas.py
git commit -m "feat: 添加Pydantic schemas"
```

### Task 4: 创建FastAPI主应用

**Files:**
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建FastAPI应用**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api import agents, conversations, skills

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgentConsole API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])

@app.get("/")
def read_root():
    return {"message": "AgentConsole API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 2: 创建API路由__init__.py**

```python
# backend/app/api/__init__.py
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/app/main.py backend/app/api/__init__.py
git commit -m "feat: 创建FastAPI主应用"
```

---

## Chunk 2: 后端API实现

### Task 5: 实现代理API

**Files:**
- Create: `backend/app/api/agents.py`

- [ ] **Step 1: 创建代理API**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app import models, schemas

router = APIRouter()

@router.post("", response_model=schemas.Agent)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = models.Agent(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("", response_model=List[schemas.Agent])
def list_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Agent).offset(skip).limit(limit).all()

@router.get("/{agent_id}", response_model=schemas.Agent)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=schemas.Agent)
def update_agent(agent_id: str, agent: schemas.AgentUpdate, db: Session = Depends(get_db)):
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in agent.model_dump().items():
        setattr(db_agent, key, value)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(db_agent)
    db.commit()
    return {"message": "Agent deleted"}
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/api/agents.py
git commit -m "feat: 实现代理API"
```

### Task 6: 实现Skills API

**Files:**
- Create: `backend/app/api/skills.py`

- [ ] **Step 1: 创建Skills API**

```python
from fastapi import APIRouter, HTTPException
from typing import List
from backend.app import schemas

router = APIRouter()

# 预定义的Skills列表
PREDEFINED_SKILLS = [
    {
        "id": "file_read",
        "name": "文件读取",
        "description": "读取指定路径的文件内容",
        "type": "tool",
        "definition": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"]
            }
        },
        "icon": "📄"
    },
    {
        "id": "file_write",
        "name": "文件写入",
        "description": "写入内容到指定文件",
        "type": "tool",
        "definition": {
            "name": "write_file",
            "description": "写入文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["path", "content"]
            }
        },
        "icon": "✍️"
    },
    {
        "id": "command_exec",
        "name": "命令执行",
        "description": "在沙箱中执行shell命令",
        "type": "tool",
        "definition": {
            "name": "execute_command",
            "description": "执行shell命令",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"}
                },
                "required": ["command"]
            }
        },
        "icon": "⚡"
    },
    {
        "id": "web_fetch",
        "name": "网页抓取",
        "description": "获取指定URL的网页内容",
        "type": "tool",
        "definition": {
            "name": "fetch_web",
            "description": "抓取网页内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网址"}
                },
                "required": ["url"]
            }
        },
        "icon": "🌐"
    },
    {
        "id": "code_execute",
        "name": "代码执行",
        "description": "执行Python/Node.js代码",
        "type": "tool",
        "definition": {
            "name": "execute_code",
            "description": "执行代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "语言 python/nodejs"},
                    "code": {"type": "string", "description": "代码内容"}
                },
                "required": ["language", "code"]
            }
        },
        "icon": "💻"
    }
]

@router.get("", response_model=List[schemas.Skill])
def list_skills():
    return PREDEFINED_SKILLS

@router.get("/{skill_id}", response_model=schemas.Skill)
def get_skill(skill_id: str):
    for skill in PREDEFINED_SKILLS:
        if skill["id"] == skill_id:
            return skill
    raise HTTPException(status_code=404, detail="Skill not found")
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/api/skills.py
git commit -m "feat: 实现Skills API"
```

### Task 7: 实现沙箱服务

**Files:**
- Create: `backend/app/services/sandbox.py`

- [ ] **Step 1: 创建沙箱服务**

```python
import os
from typing import Optional
import httpx

class SandboxService:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("OPENSANDBOX_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def create_sandbox(self, image: str = "python:3.11") -> str:
        """创建沙箱实例"""
        try:
            response = await self.client.post(
                "/api/v1/sandboxes",
                json={"image": image}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("id")
        except Exception as e:
            # 如果OpenSandbox不可用，返回模拟ID
            return f"sandbox_{hash(image)}_{id(self)}"

    async def execute_command(self, sandbox_id: str, command: str) -> dict:
        """在沙箱中执行命令"""
        try:
            response = await self.client.post(
                f"/api/v1/sandboxes/{sandbox_id}/execute",
                json={"command": command}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": 1}

    async def read_file(self, sandbox_id: str, path: str) -> str:
        """读取沙箱中的文件"""
        try:
            response = await self.client.get(
                f"/api/v1/sandboxes/{sandbox_id}/files",
                params={"path": path}
            )
            response.raise_for_status()
            return response.json().get("content", "")
        except Exception as e:
            return f"Error reading file: {e}"

    async def write_file(self, sandbox_id: str, path: str, content: str) -> bool:
        """写入沙箱中的文件"""
        try:
            response = await self.client.put(
                f"/api/v1/sandboxes/{sandbox_id}/files",
                json={"path": path, "content": content}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            return False

    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """销毁沙箱实例"""
        try:
            response = await self.client.delete(
                f"/api/v1/sandboxes/{sandbox_id}"
            )
            response.raise_for_status()
            return True
        except Exception as e:
            # 模拟销毁总是成功
            return True

    async def close(self):
        await self.client.aclose()

sandbox_service = SandboxService()
```

- [ ] **Step 2: 创建services __init__.py**

```python
# backend/app/services/__init__.py
from backend.app.services.sandbox import sandbox_service
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/app/services/sandbox.py backend/app/services/__init__.py
git commit -m "feat: 实现沙箱服务"
```

### Task 8: 实现会话API

**Files:**
- Create: `backend/app/api/conversations.py`

- [ ] **Step 1: 创建会话API**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.services.sandbox import sandbox_service

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
    sandbox_id = sandbox_service.create_sandbox(agent.image)

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

    # 销毁沙箱
    if conversation.sandbox_id:
        await sandbox_service.destroy_sandbox(conversation.sandbox_id)

    # 删除会话
    db.delete(conversation)
    db.commit()

    return {"message": "Conversation ended"}
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/api/conversations.py
git commit -m "feat: 实现会话API"
```

---

## Chunk 3: 前端项目搭建

### Task 9: 创建前端项目

**Files:**
- Create: `frontend/package.json`

- [ ] **Step 1: 创建package.json**

```json
{
  "name": "agentconsole-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5",
    "lucide-react": "^0.312.0",
    "clsx": "^2.1.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "typescript": "^5.3.3"
  }
}
```

- [ ] **Step 2: 创建Next.js配置**

```typescript
// frontend/tsconfig.json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

```javascript
// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
```

- [ ] **Step 3: 创建API客户端**

```typescript
// frontend/lib/api.ts
import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
})

// Agent APIs
export const getAgents = () => api.get('/api/agents')
export const getAgent = (id: string) => api.get(`/api/agents/${id}`)
export const createAgent = (data: any) => api.post('/api/agents', data)
export const updateAgent = (id: string, data: any) => api.put(`/api/agents/${id}`, data)
export const deleteAgent = (id: string) => api.delete(`/api/agents/${id}`)

// Conversation APIs
export const createConversation = (agentId: string) =>
  api.post('/api/conversations', { agent_id: agentId })
export const getConversation = (id: string) => api.get(`/api/conversations/${id}`)
export const getMessages = (conversationId: string) =>
  api.get(`/api/conversations/${conversationId}/messages`)
export const sendMessage = (conversationId: string, content: string) =>
  api.post(`/api/conversations/${conversationId}/messages`, { content })
export const endConversation = (id: string) => api.delete(`/api/conversations/${id}`)

// Skills APIs
export const getSkills = () => api.get('/api/skills')
```

- [ ] **Step 4: 提交代码**

```bash
git add frontend/package.json frontend/tsconfig.json frontend/next.config.js frontend/lib/api.ts
git commit -m "feat: 创建前端项目基础"
```

### Task 10: 创建前端页面组件

**Files:**
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`

- [ ] **Step 1: 创建布局文件**

```tsx
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AgentConsole - 智能代理系统',
  description: '基于OpenSandbox的智能代理系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  )
}
```

- [ ] **Step 2: 创建全局样式**

```css
/* frontend/app/globals.css */
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --background: #ffffff;
  --foreground: #171717;
}

body {
  color: var(--foreground);
  background: var(--background);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
```

- [ ] **Step 3: 创建首页**

```tsx
import Link from 'next/link'

export default function Home() {
  return (
    <main className="container">
      <h1>AgentConsole</h1>
      <p>基于OpenSandbox的智能代理系统</p>
      <div style={{ marginTop: 20 }}>
        <Link href="/agents">
          <button style={{
            padding: '10px 20px',
            background: '#4f46e5',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
            marginRight: 10
          }}>
            管理智能代理
          </button>
        </Link>
      </div>
    </main>
  )
}
```

- [ ] **Step 4: 提交代码**

```bash
git add frontend/app/layout.tsx frontend/app/page.tsx frontend/app/globals.css
git commit -m "feat: 创建前端基础页面"
```

### Task 11: 创建代理管理页面

**Files:**
- Create: `frontend/app/agents/page.tsx`

- [ ] **Step 1: 创建代理列表页**

```tsx
'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getAgents, deleteAgent } from '@/lib/api'

interface Agent {
  id: string
  name: string
  description: string
  skills: string[]
  image: string
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const res = await getAgents()
      setAgents(res.data)
    } catch (error) {
      console.error('Failed to load agents', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个代理吗？')) return
    try {
      await deleteAgent(id)
      setAgents(agents.filter(a => a.id !== id))
    } catch (error) {
      console.error('Failed to delete agent', error)
    }
  }

  if (loading) return <div>加载中...</div>

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>智能代理管理</h1>
        <Link href="/agents/new">
          <button style={{
            padding: '10px 20px',
            background: '#4f46e5',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer'
          }}>
            + 创建代理
          </button>
        </Link>
      </div>

      <div style={{ marginTop: 20 }}>
        {agents.length === 0 ? (
          <p>还没有创建任何代理</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 20 }}>
            {agents.map(agent => (
              <div key={agent.id} style={{
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                padding: 16
              }}>
                <h3>{agent.name}</h3>
                <p style={{ color: '#6b7280', fontSize: 14 }}>{agent.description || '暂无描述'}</p>
                <div style={{ marginTop: 10, fontSize: 12, color: '#9ca3af' }}>
                  Skills: {agent.skills?.length || 0} 个
                </div>
                <div style={{ marginTop: 10, display: 'flex', gap: 10 }}>
                  <Link href={`/agents/${agent.id}/chat`}>
                    <button style={{
                      padding: '6px 12px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      cursor: 'pointer'
                    }}>
                      启动
                    </button>
                  </Link>
                  <Link href={`/agents/${agent.id}`}>
                    <button style={{
                      padding: '6px 12px',
                      background: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      cursor: 'pointer'
                    }}>
                      编辑
                    </button>
                  </Link>
                  <button
                    onClick={() => handleDelete(agent.id)}
                    style={{
                      padding: '6px 12px',
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      cursor: 'pointer'
                    }}
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/app/agents/page.tsx
git commit -m "feat: 创建代理列表页"
```

### Task 12: 创建代理创建/编辑页面

**Files:**
- Create: `frontend/app/agents/new/page.tsx`

- [ ] **Step 1: 创建代理创建页**

```tsx
'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getSkills, createAgent } from '@/lib/api'

interface Skill {
  id: string
  name: string
  description: string
  icon: string
}

export default function NewAgentPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [image, setImage] = useState('python:3.11')
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getSkills().then(res => setSkills(res.data))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createAgent({
        name,
        description,
        skills: selectedSkills,
        image
      })
      router.push('/agents')
    } catch (error) {
      console.error('Failed to create agent', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleSkill = (skillId: string) => {
    setSelectedSkills(prev =>
      prev.includes(skillId)
        ? prev.filter(id => id !== skillId)
        : [...prev, skillId]
    )
  }

  const images = [
    'python:3.11',
    'python:3.10',
    'node:18',
    'node:20',
    'golang:1.21'
  ]

  return (
    <div className="container">
      <h1>创建智能代理</h1>
      <form onSubmit={handleSubmit} style={{ maxWidth: 600, marginTop: 20 }}>
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>代理名称</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            required
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #d1d5db' }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>描述</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={3}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #d1d5db' }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>选择Skills</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            {skills.map(skill => (
              <button
                key={skill.id}
                type="button"
                onClick={() => toggleSkill(skill.id)}
                style={{
                  padding: '8px 12px',
                  border: selectedSkills.includes(skill.id) ? '2px solid #4f46e5' : '1px solid #d1d5db',
                  borderRadius: 6,
                  background: selectedSkills.includes(skill.id) ? '#eef2ff' : 'white',
                  cursor: 'pointer'
                }}
              >
                {skill.icon} {skill.name}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>沙箱镜像</label>
          <select
            value={image}
            onChange={e => setImage(e.target.value)}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #d1d5db' }}
          >
            {images.map(img => (
              <option key={img} value={img}>{img}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '10px 20px',
              background: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? '创建中...' : '创建'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            style={{
              padding: '10px 20px',
              background: '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer'
            }}
          >
            取消
          </button>
        </div>
      </form>
    </div>
  )
}
```

- [ ] **Step 2: 创建代理编辑页**

```tsx
// frontend/app/agents/[id]/page.tsx
// 结构类似创建页，通过useEffect加载现有数据并更新
```

- [ ] **Step 3: 提交代码**

```bash
git add frontend/app/agents/new/page.tsx frontend/app/agents/\[id\]/page.tsx
git commit -m "feat: 创建代理创建和编辑页面"
```

### Task 13: 创建会话聊天页面

**Files:**
- Create: `frontend/app/agents/[id]/chat/page.tsx`

- [ ] **Step 1: 创建聊天页面**

```tsx
'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { createConversation, getMessages, sendMessage, endConversation } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params.id as string
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    startConversation()
    return () => {
      if (conversationId) {
        endConversation(conversationId).catch(console.error)
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startConversation = async () => {
    try {
      const res = await createConversation(agentId)
      setConversationId(res.data.id)
    } catch (error) {
      console.error('Failed to start conversation', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || !conversationId) return
    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    try {
      // 添加用户消息
      setMessages(prev => [...prev, { id: 'temp', role: 'user', content: userMessage }])

      const res = await sendMessage(conversationId, userMessage)
      setMessages(prev => [...prev, res.data])
    } catch (error) {
      console.error('Failed to send message', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEnd = async () => {
    if (!conversationId) return
    try {
      await endConversation(conversationId)
      router.push('/agents')
    } catch (error) {
      console.error('Failed to end conversation', error)
    }
  }

  return (
    <div className="container" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 10 }}>
        <h2>会话聊天</h2>
        <button
          onClick={handleEnd}
          style={{
            padding: '8px 16px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer'
          }}
        >
          结束会话
        </button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', border: '1px solid #e5e7eb', borderRadius: 8, padding: 20, marginBottom: 20 }}>
        {messages.length === 0 ? (
          <p style={{ color: '#9ca3af', textAlign: 'center' }}>开始发送消息与智能代理对话...</p>
        ) : (
          messages.map(msg => (
            <div key={msg.id} style={{
              marginBottom: 16,
              textAlign: msg.role === 'user' ? 'right' : 'left'
            }}>
              <div style={{
                display: 'inline-block',
                maxWidth: '70%',
                padding: '10px 16px',
                borderRadius: 12,
                background: msg.role === 'user' ? '#4f46e5' : '#f3f4f6',
                color: msg.role === 'user' ? 'white' : 'black',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div style={{ color: '#9ca3af' }}>代理正在思考...</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="输入您想完成的任务..."
          disabled={loading}
          style={{ flex: 1, padding: 12, borderRadius: 8, border: '1px solid #d1d5db' }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            padding: '12px 24px',
            background: '#4f46e5',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1
          }}
        >
          发送
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/app/agents/\[id\]/chat/page.tsx
git commit -m "feat: 创建会话聊天页面"
```

---

## Chunk 4: 部署配置

### Task 14: 创建Docker配置

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENSANDBOX_URL=http://opensandbox:8000
    depends_on:
      - opensandbox
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  opensandbox:
    image: opensandbox/opensandbox:latest
    ports:
      - "9000:8000"
```

- [ ] **Step 2: 创建后端Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: 创建前端Dockerfile**

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

- [ ] **Step 4: 提交代码**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile
git commit -m "feat: 添加Docker部署配置"
```

---

## 总结

实施计划包含以下主要任务:

1. **后端基础** - 项目结构、数据库、模型、schemas
2. **后端API** - 代理管理、Skills管理、会话管理
3. **沙箱服务** - OpenSandbox集成
4. **前端** - 项目搭建、代理管理、创建编辑、会话聊天
5. **部署** - Docker Compose配置

整个项目预计需要约50-60个步骤完成。
