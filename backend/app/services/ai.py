import os
import json
from typing import List, Dict, Any, Optional
import httpx

class AIService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.base_url = "https://api.anthropic.com/v1"
        self.model = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:
        """发送聊天请求到Claude API"""
        if not self.api_key:
            return self._mock_response(messages)

        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                formatted_messages.append({"role": "assistant", "content": msg["content"]})

        # 构建请求
        request_body = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": formatted_messages,
        }

        # 如果有工具，添加工具定义
        if tools:
            request_body["tools"] = tools

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json=request_body,
                    timeout=120.0
                )

                if response.status_code != 200:
                    return self._mock_response(messages)

                result = response.json()
                return self._parse_response(result)
        except Exception as e:
            print(f"AI API error: {e}")
            return self._mock_response(messages)

    def _parse_response(self, result: Dict) -> Dict[str, Any]:
        """解析API响应"""
        content = result.get("content", [])

        # 检查是否有工具调用
        tool_calls = []
        text_content = ""

        for block in content:
            if block.get("type") == "tool_use":
                tool_calls.append({
                    "name": block.get("name"),
                    "input": block.get("input", {}),
                    "id": block.get("id")
                })
            elif block.get("type") == "text":
                text_content += block.get("text", "")

        return {
            "content": text_content,
            "tool_calls": tool_calls
        }

    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """模拟响应（当API不可用时）"""
        last_message = messages[-1]["content"] if messages else ""

        responses = {
            "content": f"我收到了您的请求: {last_message[:50]}...\n\n正在分析任务并准备执行。由于AI服务暂未配置，当前为模拟响应。在实际环境中，我将分析您的需求，使用可用的工具在沙箱中完成相应操作，并返回结果。",
            "tool_calls": []
        }
        return responses

    def build_system_prompt(self, agent_name: str, agent_description: str, skills: List[Dict]) -> str:
        """构建系统提示词"""
        skills_description = "\n".join([
            f"- {s['name']}: {s['description']}"
            for s in skills
        ])

        tools_definition = "\n".join([
            f"## {s['name']} ({s['id']})\n{s.get('definition', {}).get('description', '')}"
            for s in skills
        ])

        return f"""你是{agent_name}，一个智能代理。

## 角色描述
{agent_description}

## 可用技能
{skills_description}

## 工具定义
{tools_definition}

## 工作流程
1. 理解用户请求
2. 确定需要使用的技能
3. 在沙箱中执行相应操作
4. 返回结果给用户

## 重要约束
- 所有操作必须在沙箱中执行
- 不要直接操作本地文件系统
- 使用提供的工具与沙箱交互
- 保持回复简洁明了"""


# 全局AI服务实例
ai_service = AIService()
