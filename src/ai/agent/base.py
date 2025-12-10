"""
智能体基类 - Agent 框架（预留）
"""
from abc import ABC, abstractmethod
from typing import Any, List


class BaseAgent(ABC):
    """Agent 抽象基类"""
    
    @abstractmethod
    async def run(self, input: str, **kwargs) -> str:
        """运行智能体"""
        pass
    
    @abstractmethod
    def add_tool(self, tool: Any) -> None:
        """添加工具"""
        pass
    
    @property
    @abstractmethod
    def tools(self) -> List[Any]:
        """获取所有工具"""
        pass


