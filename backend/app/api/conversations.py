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
    # 文件操作
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
        "id": "file_list",
        "name": "文件列表",
        "description": "列出目录中的文件",
        "type": "tool",
        "definition": {
            "name": "list_files",
            "description": "列出目录中的文件",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径", "default": "/workspace"}
                },
                "required": []
            }
        },
        "icon": "📁"
    },
    # 命令执行
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
    # 网络
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
        "id": "download_file",
        "name": "文件下载",
        "description": "从URL下载文件到沙箱",
        "type": "tool",
        "definition": {
            "name": "download_file",
            "description": "从URL下载文件",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "文件URL"},
                    "path": {"type": "string", "description": "保存路径"}
                },
                "required": ["url", "path"]
            }
        },
        "icon": "📥"
    },
    # 代码执行
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
    },
    # Git操作
    {
        "id": "git_clone",
        "name": "Git克隆",
        "description": "克隆Git仓库到沙箱",
        "type": "tool",
        "definition": {
            "name": "git_clone",
            "description": "克隆Git仓库",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Git仓库URL"},
                    "path": {"type": "string", "description": "克隆到的目录", "default": "/workspace"}
                },
                "required": ["url"]
            }
        },
        "icon": "📦"
    },
    {
        "id": "git_command",
        "name": "Git命令",
        "description": "执行Git命令",
        "type": "tool",
        "definition": {
            "name": "git_command",
            "description": "执行Git命令",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Git命令(不带git前缀)"},
                    "path": {"type": "string", "description": "仓库路径", "default": "/workspace"}
                },
                "required": ["command"]
            }
        },
        "icon": "🔀"
    },
    # 数据处理
    {
        "id": "json_parse",
        "name": "JSON解析",
        "description": "解析和操作JSON数据",
        "type": "tool",
        "definition": {
            "name": "parse_json",
            "description": "解析JSON数据",
            "input_schema": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON字符串"},
                    "operation": {"type": "string", "description": "操作: parse/format/query", "enum": ["parse", "format", "query"]},
                    "query": {"type": "string", "description": "JMESPath查询(可选)"}
                },
                "required": ["data", "operation"]
            }
        },
        "icon": "🔧"
    },
    # 包管理
    {
        "id": "pip_install",
        "name": "Python包安装",
        "description": "安装Python包",
        "type": "tool",
        "definition": {
            "name": "pip_install",
            "description": "安装Python包",
            "input_schema": {
                "type": "object",
                "properties": {
                    "packages": {"type": "string", "description": "包名(空格分隔)"}
                },
                "required": ["packages"]
            }
        },
        "icon": "🐍"
    },
    {
        "id": "npm_install",
        "name": "NPM包安装",
        "description": "安装Node.js包",
        "type": "tool",
        "definition": {
            "name": "npm_install",
            "description": "安装Node.js包",
            "input_schema": {
                "type": "object",
                "properties": {
                    "packages": {"type": "string", "description": "包名(空格分隔)"},
                    "path": {"type": "string", "description": "项目路径", "default": "/workspace"}
                },
                "required": ["packages"]
            }
        },
        "icon": "📦"
    },
]
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

    # 文件操作
    if tool_name == "read_file":
        result = await sandbox_service.read_file(sandbox_id, tool_input.get("path", ""))

    elif tool_name == "write_file":
        success = await sandbox_service.write_file(
            sandbox_id,
            tool_input.get("path", ""),
            tool_input.get("content", "")
        )
        result = "文件写入成功" if success else "文件写入失败"

    elif tool_name == "list_files":
        path = tool_input.get("path", "/workspace")
        files = await sandbox_service.list_files(sandbox_id, path)
        result = "文件列表:\n" + "\n".join(f"  - {f}" for f in files)

    # 命令执行
    elif tool_name == "execute_command":
        result = await sandbox_service.execute_command(sandbox_id, tool_input.get("command", ""))

    # 网络操作
    elif tool_name == "fetch_web":
        url = tool_input.get("url", "")
        cmd_result = await sandbox_service.execute_command(sandbox_id, f"curl -sL '{url}' | head -200")
        result = cmd_result.get("stdout", cmd_result.get("stderr", ""))

    elif tool_name == "download_file":
        url = tool_input.get("url", "")
        path = tool_input.get("path", "/workspace")
        cmd_result = await sandbox_service.execute_command(
            sandbox_id,
            f"curl -sL '{url}' -o '{path}' && echo 'Downloaded to {path}'"
        )
        result = cmd_result.get("stdout", cmd_result.get("stderr", ""))

    # 代码执行
    elif tool_name == "execute_code":
        language = tool_input.get("language", "python")
        code = tool_input.get("code", "")

        if language == "python":
            # 写入临时文件执行以便处理复杂代码
            await sandbox_service.write_file(sandbox_id, "/tmp/script.py", code)
            cmd_result = await sandbox_service.execute_command(sandbox_id, "python3 /tmp/script.py")
        elif language == "nodejs":
            await sandbox_service.write_file(sandbox_id, "/tmp/script.js", code)
            cmd_result = await sandbox_service.execute_command(sandbox_id, "node /tmp/script.js")
        else:
            return f"不支持的语言: {language}"

        result = f"stdout:\n{cmd_result.get('stdout', '')}\nstderr:\n{cmd_result.get('stderr', '')}\nexit_code: {cmd_result.get('exit_code', 0)}"

    # Git操作
    elif tool_name == "git_clone":
        url = tool_input.get("url", "")
        path = tool_input.get("path", "/workspace")
        cmd_result = await sandbox_service.execute_command(
            sandbox_id,
            f"git clone '{url}' '{path}'"
        )
        result = cmd_result.get("stdout", cmd_result.get("stderr", ""))

    elif tool_name == "git_command":
        command = tool_input.get("command", "")
        path = tool_input.get("path", "/workspace")
        cmd_result = await sandbox_service.execute_command(
            sandbox_id,
            f"cd '{path}' && git {command}"
        )
        result = f"stdout:\n{cmd_result.get('stdout', '')}\nstderr:\n{cmd_result.get('stderr', '')}\nexit_code: {cmd_result.get('exit_code', 0)}"

    # 数据处理
    elif tool_name == "parse_json":
        import json
        data_str = tool_input.get("data", "{}")
        operation = tool_input.get("operation", "parse")

        try:
            data = json.loads(data_str)
            if operation == "format":
                result = json.dumps(data, indent=2, ensure_ascii=False)
            elif operation == "query":
                # 简单查询 - 支持key路径如 "data.users.0.name"
                query = tool_input.get("query", "")
                parts = query.split(".")
                current = data
                for part in parts:
                    if part.isdigit():
                        current = current[int(part)]
                    else:
                        current = current.get(part, {})
                result = json.dumps(current, indent=2, ensure_ascii=False) if current else "Not found"
            else:
                result = json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            result = f"JSON解析错误: {e}"

    # 包管理
    elif tool_name == "pip_install":
        packages = tool_input.get("packages", "")
        cmd_result = await sandbox_service.execute_command(
            sandbox_id,
            f"pip install {packages}"
        )
        result = f"stdout:\n{cmd_result.get('stdout', '')}\nstderr:\n{cmd_result.get('stderr', '')}\nexit_code: {cmd_result.get('exit_code', 0)}"

    elif tool_name == "npm_install":
        packages = tool_input.get("packages", "")
        path = tool_input.get("path", "/workspace")
        cmd_result = await sandbox_service.execute_command(
            sandbox_id,
            f"cd '{path}' && npm install {packages}"
        )
        result = f"stdout:\n{cmd_result.get('stdout', '')}\nstderr:\n{cmd_result.get('stderr', '')}\nexit_code: {cmd_result.get('exit_code', 0)}"

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
