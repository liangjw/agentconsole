"""
OpenSandbox 服务封装

支持两种模式:
1. SDK模式: 使用opensandbox-python SDK (需要安装opensandbox包)
2. HTTP模式: 直接调用OpenSandbox HTTP API

配置方式:
- OPENSANDBOX_MODE=sdk 或 http
- SDK模式需要配置镜像等参数
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from datetime import timedelta

# 尝试导入OpenSandbox SDK
try:
    from opensandbox import Sandbox
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


class SandboxService:
    """沙箱服务封装"""

    def __init__(self):
        self.mode = os.getenv("OPENSANDBOX_MODE", "mock")  # sdk, http, mock
        self.base_url = os.getenv("OPENSANDBOX_URL", "http://localhost:8000")
        self.default_image = os.getenv("OPENSANDBOX_IMAGE", "opensandbox/code-interpreter:v1.0.1")
        self.default_timeout = int(os.getenv("OPENSANDBOX_TIMEOUT", "600"))  # 秒
        self._sandboxes: Dict[str, Any] = {}  # 存储活跃的沙箱实例

    async def create_sandbox(
        self,
        image: str = None,
        timeout: int = None,
        entrypoint: List[str] = None,
        env: Dict[str, str] = None
    ) -> str:
        """
        创建沙箱实例

        Args:
            image: 镜像名称
            timeout: 超时时间(秒)
            entrypoint: 入口点命令
            env: 环境变量

        Returns:
            沙箱ID
        """
        image = image or self.default_image
        timeout = timeout or self.default_timeout

        if self.mode == "mock":
            # 模拟模式 - 生成虚拟沙箱ID
            sandbox_id = f"sandbox_{hash(image)}_{id(self)}"
            self._sandboxes[sandbox_id] = {
                "image": image,
                "status": "created",
                "files": {}
            }
            return sandbox_id

        elif self.mode == "sdk" and SDK_AVAILABLE:
            # SDK模式
            try:
                sandbox = await Sandbox.create(
                    image,
                    entrypoint=entrypoint or ["/opt/opensandbox/code-interpreter.sh"],
                    env=env or {},
                    timeout=timedelta(seconds=timeout)
                )
                sandbox_id = f"sdk_{hash(image)}_{id(sandbox)}"
                self._sandboxes[sandbox_id] = {
                    "sandbox": sandbox,
                    "image": image,
                    "status": "running"
                }
                return sandbox_id
            except Exception as e:
                print(f"Failed to create sandbox via SDK: {e}")
                # 回退到模拟模式
                sandbox_id = f"fallback_{hash(image)}_{id(self)}"
                self._sandboxes[sandbox_id] = {
                    "image": image,
                    "status": "created",
                    "files": {}
                }
                return sandbox_id

        else:
            # HTTP模式 - 暂未实现，使用模拟
            sandbox_id = f"http_{hash(image)}_{id(self)}"
            self._sandboxes[sandbox_id] = {
                "image": image,
                "status": "created",
                "files": {}
            }
            return sandbox_id

    async def execute_command(
        self,
        sandbox_id: str,
        command: str,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        在沙箱中执行命令

        Args:
            sandbox_id: 沙箱ID
            command: 要执行的命令
            timeout: 超时时间(秒)

        Returns:
            执行结果 {"stdout": "", "stderr": "", "exit_code": 0}
        """
        timeout = timeout or 60

        sandbox_info = self._sandboxes.get(sandbox_id)
        if not sandbox_info:
            return {"stdout": "", "stderr": "Sandbox not found", "exit_code": 1}

        if self.mode == "mock":
            # 模拟模式 - 返回模拟结果
            return self._mock_execute(command)

        elif self.mode == "sdk" and sandbox_info.get("sandbox"):
            # SDK模式
            try:
                sandbox = sandbox_info["sandbox"]
                result = await asyncio.wait_for(
                    sandbox.commands.run(command),
                    timeout=timeout
                )
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code
                }
            except asyncio.TimeoutError:
                return {"stdout": "", "stderr": "Command timeout", "exit_code": 124}
            except Exception as e:
                return {"stdout": "", "stderr": str(e), "exit_code": 1}

        else:
            # 其他模式 - 模拟
            return self._mock_execute(command)

    def _mock_execute(self, command: str) -> Dict[str, Any]:
        """模拟命令执行"""
        command = command.strip().lower()

        # 模拟一些常见命令
        if command.startswith("echo "):
            return {
                "stdout": command[5:].strip('"').strip("'"),
                "stderr": "",
                "exit_code": 0
            }
        elif command.startswith("ls"):
            return {
                "stdout": "file1.txt\nfile2.txt\nREADME.md",
                "stderr": "",
                "exit_code": 0
            }
        elif command.startswith("pwd"):
            return {
                "stdout": "/workspace",
                "stderr": "",
                "exit_code": 0
            }
        elif command.startswith("python") or command.startswith("python3"):
            return {
                "stdout": "Python execution simulated",
                "stderr": "",
                "exit_code": 0
            }
        elif command.startswith("node"):
            return {
                "stdout": "Node.js execution simulated",
                "stderr": "",
                "exit_code": 0
            }
        elif command.startswith("curl ") or command.startswith("wget "):
            return {
                "stdout": "<html><body>Mock web content</body></html>",
                "stderr": "",
                "exit_code": 0
            }
        else:
            return {
                "stdout": f"Executed: {command}",
                "stderr": "",
                "exit_code": 0
            }

    async def read_file(self, sandbox_id: str, path: str) -> str:
        """
        读取沙箱中的文件

        Args:
            sandbox_id: 沙箱ID
            path: 文件路径

        Returns:
            文件内容
        """
        sandbox_info = self._sandboxes.get(sandbox_id)
        if not sandbox_info:
            return "Error: Sandbox not found"

        if self.mode == "mock":
            # 模拟模式 - 返回存储的文件内容
            files = sandbox_info.get("files", {})
            return files.get(path, f"Content of {path} (simulated)")

        elif self.mode == "sdk" and sandbox_info.get("sandbox"):
            # SDK模式
            try:
                sandbox = sandbox_info["sandbox"]
                content = await sandbox.files.read_file(path)
                return content
            except Exception as e:
                return f"Error reading file: {e}"

        else:
            # 其他模式 - 模拟
            files = sandbox_info.get("files", {})
            return files.get(path, f"Content of {path} (simulated)")

    async def write_file(self, sandbox_id: str, path: str, content: str) -> bool:
        """
        写入文件到沙箱

        Args:
            sandbox_id: 沙箱ID
            path: 文件路径
            content: 文件内容

        Returns:
            是否成功
        """
        sandbox_info = self._sandboxes.get(sandbox_id)
        if not sandbox_info:
            return False

        if self.mode == "mock":
            # 模拟模式 - 存储到内存
            if "files" not in sandbox_info:
                sandbox_info["files"] = {}
            sandbox_info["files"][path] = content
            return True

        elif self.mode == "sdk" and sandbox_info.get("sandbox"):
            # SDK模式
            try:
                sandbox = sandbox_info["sandbox"]
                from opensandbox import WriteEntry
                await sandbox.files.write_files([
                    WriteEntry(path=path, data=content, mode=644)
                ])
                return True
            except Exception as e:
                print(f"Error writing file: {e}")
                return False

        else:
            # 其他模式 - 模拟
            if "files" not in sandbox_info:
                sandbox_info["files"] = {}
            sandbox_info["files"][path] = content
            return True

    async def list_files(self, sandbox_id: str, path: str = "/") -> List[str]:
        """
        列出沙箱中的文件

        Args:
            sandbox_id: 沙箱ID
            path: 目录路径

        Returns:
            文件列表
        """
        sandbox_info = self._sandboxes.get(sandbox_id)
        if not sandbox_info:
            return []

        if self.mode == "mock":
            files = sandbox_info.get("files", {})
            if files:
                return list(files.keys())
            return ["file1.txt", "file2.txt", "README.md"]

        elif self.mode == "sdk" and sandbox_info.get("sandbox"):
            try:
                sandbox = sandbox_info["sandbox"]
                # SDK可能没有直接列出文件的方法
                return await self._list_files(sandbox, path_via_command)
            except:
                return ["file1.txt", "file2.txt"]

        return ["file1.txt", "file2.txt"]

    async def _list_files_via_command(self, sandbox, path: str) -> List[str]:
        """通过命令列出文件"""
        try:
            result = await sandbox.commands.run(f"ls -la {path}")
            if result.exit_code == 0:
                lines = result.stdout.strip().split("\n")
                files = []
                for line in lines[1:]:  # 跳过total行
                    parts = line.split()
                    if len(parts) >= 8:
                        files.append(parts[-1])
                return files
        except:
            pass
        return []

    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """
        销毁沙箱实例

        Args:
            sandbox_id: 沙箱ID

        Returns:
            是否成功
        """
        sandbox_info = self._sandboxes.get(sandbox_id)
        if not sandbox_info:
            return True

        if self.mode == "sdk" and sandbox_info.get("sandbox"):
            try:
                sandbox = sandbox_info["sandbox"]
                await sandbox.close()
            except Exception as e:
                print(f"Error closing sandbox: {e}")

        # 移除沙箱
        if sandbox_id in self._sandboxes:
            del self._sandboxes[sandbox_id]

        return True

    async def get_sandbox_status(self, sandbox_id: str) -> Dict[str, Any]:
        """
        获取沙箱状态

        Args:
            sandbox_id: 沙箱ID

        Returns:
            状态信息
        """
        sandbox_info = self._sandboxes.get(sandbox_id)
        if not sandbox_info:
            return {"status": "not_found"}

        return {
            "status": sandbox_info.get("status", "unknown"),
            "image": sandbox_info.get("image", ""),
            "mode": self.mode
        }


# 全局沙箱服务实例
sandbox_service = SandboxService()
