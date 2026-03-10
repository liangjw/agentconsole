from fastapi import APIRouter, HTTPException
from typing import List
from backend.app import schemas

router = APIRouter()

# 预设代理模板
AGENT_TEMPLATES = [
    {
        "id": "coder",
        "name": "编程助手",
        "description": "专业的编程助手，可以编写、调试代码，安装依赖包",
        "skills": ["file_read", "file_write", "command_exec", "code_execute", "pip_install", "npm_install", "git_clone"],
        "image": "python:3.11",
        "icon": "💻",
        "category": "开发"
    },
    {
        "id": "data_analyst",
        "name": "数据分析师",
        "description": "处理数据，分析文件、执行数据分析代码",
        "skills": ["file_read", "file_write", "command_exec", "code_execute", "pip_install", "json_parse"],
        "image": "python:3.11",
        "icon": "📊",
        "category": "分析"
    },
    {
        "id": "researcher",
        "name": "研究员",
        "description": "搜集网络信息、抓取网页、整理研究资料",
        "skills": ["web_fetch", "file_write", "command_exec", "json_parse"],
        "image": "python:3.11",
        "icon": "🔬",
        "category": "研究"
    },
    {
        "id": "web_developer",
        "name": "Web开发者",
        "description": "创建Web应用、安装npm包、运行开发服务器",
        "skills": ["file_read", "file_write", "command_exec", "npm_install", "git_clone", "execute_code"],
        "image": "node:20",
        "icon": "🌐",
        "category": "开发"
    },
    {
        "id": "scraper",
        "name": "网页爬虫",
        "description": "抓取网页内容、下载文件、处理数据",
        "skills": ["web_fetch", "download_file", "file_write", "command_exec", "code_execute"],
        "image": "python:3.11",
        "icon": "🕷️",
        "category": "工具"
    },
    {
        "id": "file_manager",
        "name": "文件管理器",
        "description": "管理文件、读写文件、列出目录内容",
        "skills": ["file_read", "file_write", "file_list", "command_exec"],
        "image": "python:3.11",
        "icon": "📁",
        "category": "工具"
    },
    {
        "id": "git_assistant",
        "name": "Git助手",
        "description": "克隆仓库、执行Git命令、帮助理解代码库",
        "skills": ["git_clone", "git_command", "file_read", "command_exec"],
        "image": "python:3.11",
        "icon": "🔀",
        "category": "开发"
    },
    {
        "id": "general",
        "name": "通用助手",
        "description": "处理各种任务的通用助手",
        "skills": ["file_read", "file_write", "command_exec", "web_fetch", "code_execute"],
        "image": "python:3.11",
        "icon": "🤖",
        "category": "通用"
    }
]

@router.get("", response_model=List[schemas.AgentTemplate])
def list_templates():
    """获取所有代理模板"""
    return AGENT_TEMPLATES

@router.get("/categories")
def list_categories():
    """获取所有模板分类"""
    categories = list(set(t["category"] for t in AGENT_TEMPLATES))
    return {"categories": categories}

@router.get("/{template_id}", response_model=schemas.AgentTemplate)
def get_template(template_id: str):
    """获取指定模板"""
    for template in AGENT_TEMPLATES:
        if template["id"] == template_id:
            return template
    raise HTTPException(status_code=404, detail="Template not found")
