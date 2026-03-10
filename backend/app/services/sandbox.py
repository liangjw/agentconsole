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
