from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.services.ai import ai_service
from backend.app.services.sandbox import sandbox_service

router = APIRouter()

# 预定义的Skills定义
PREDEFINED_SKILLS = [
    {
        "id": "file_read",
        "name": "文件读取",
        "description": "读取指定路径的文件内容",
        "type": "tool",
        "definition": {
            "name": "read_file",
            "description": "读取文件内容",
            "input_schema": {
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
            "input_schema": {
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
            "input_schema": {
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
            "input_schema": {
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
            "input_schema": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "语言 python/nodejs", "enum": ["python", "nodejs"]},
                    "code": {"type": "string", "description": "代码内容"}
                },
                "required": ["language", "code"]
            }
        },
        "icon": "💻"
    }
]

def get_skill_by_id(skill_id: str) -> Dict[str, Any]:
    """根据ID获取Skill定义"""
    for skill in PREDEFINED_SKILLS:
        if skill["id"] == skill_id:
            return skill
    return None

def convert_skills_to_tools(skills: List[str]) -> List[Dict[str, Any]]:
    """将Skills转换为Claude工具格式"""
    tools = []
    for skill_id in skills:
        skill = get_skill_by_id(skill_id)
        if skill and skill.get("definition"):
            tools.append({
                "name": skill["definition"].get("name", skill_id),
                "description": skill["definition"].get("description", ""),
                "input_schema": skill["definition"].get("input_schema", {})
            })
    return tools

async def execute_tool(tool_name: str, tool_input: Dict[str, Any], sandbox_id: str) -> str:
    """执行工具调用"""
    result = ""

    if tool_name == "read_file":
        result = await sandbox_service.read_file(sandbox_id, tool_input.get("path", ""))

    elif tool_name == "write_file":
        success = await sandbox_service.write_file(
            sandbox_id,
            tool_input.get("path", ""),
            tool_input.get("content", "")
        )
        result = "文件写入成功" if success else "文件写入失败"

    elif tool_name == "execute_command":
        result = await sandbox_service.execute_command(sandbox_id, tool_input.get("command", ""))

    elif tool_name == "fetch_web":
        # 使用curl获取网页
        url = tool_input.get("url", "")
        cmd_result = await sandbox_service.execute_command(sandbox_id, f"curl -s '{url}' | head -100")
        result = cmd_result.get("stdout", cmd_result.get("stderr", ""))

    elif tool_name == "execute_code":
        language = tool_input.get("language", "python")
        code = tool_input.get("code", "")

        if language == "python":
            cmd = f'python3 -c """{code}"""'
        elif language == "nodejs":
            cmd = f'node -e "{code}"'
        else:
            return f"不支持的语言: {language}"

        result = await sandbox_service.execute_command(sandbox_id, cmd)

    else:
        result = f"未知工具: {tool_name}"

    return str(result)

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

    # 准备消息列表
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": message.content})

    # 获取代理配置的Skills并转换为工具
    agent_skills = agent.skills or []
    tools = convert_skills_to_tools(agent_skills)

    # 构建系统提示词
    system_prompt = ai_service.build_system_prompt(
        agent.name,
        agent.description,
        [s for s in PREDEFINED_SKILLS if s["id"] in agent_skills]
    )

    # 调用AI服务
    ai_response = await ai_service.chat(messages, tools, system_prompt)

    # 执行工具调用（如果有）
    tool_calls = ai_response.get("tool_calls", [])
    tool_results = []

    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "")
        tool_input = tool_call.get("input", {})

        # 执行工具
        result = await execute_tool(tool_name, tool_input, conversation.sandbox_id)
        tool_results.append({
            "tool": tool_name,
            "input": tool_input,
            "result": result
        })

    # 如果有工具调用，获取工具结果后再次调用AI
    if tool_results:
        # 添加工具结果到消息
        messages.append({
            "role": "assistant",
            "content": ai_response.get("content", "")
        })

        # 添加工具结果作为user消息
        for tr in tool_results:
            tool_result_message = f"工具 {tr['tool']} 执行结果:\n{tr['result']}"
            messages.append({"role": "user", "content": tool_result_message})

        # 再次调用AI获取最终响应
        final_response = await ai_service.chat(messages, tools, system_prompt)
        ai_response["content"] = final_response.get("content", ai_response["content"])

    # 保存代理响应
    db_response = models.Message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response.get("content", "处理完成"),
        tool_calls=tool_results
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
