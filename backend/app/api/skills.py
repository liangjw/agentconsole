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
