#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
from abc import ABC, abstractmethod
from langchain.tools import BaseTool


class Tool(BaseTool, ABC):

    def get_tool_name(self) -> str:
        """
        工具的名称，唯一值
        Returns: str, 工具的名称
        """
        return self.name

    def get_tool_desc(self) -> str:
        """
        工具的描述，用于指示LLM是否需要选择该工具
        Returns: str, 工具的描述
        """
        return self.description

    @abstractmethod
    def get_tool_principle(self) -> str:
        """
        工具使用原则，告诉模型在什么情况下使用工具
        Returns: str, 工具的Principle
        """

    @property
    def output_type(self):
        """
        工具的返回值类型，此方法可获取_run方法返回类型
        Returns: Type, 工具的返回值类型
        """
        return self._run.__annotations__["return"]

    @abstractmethod
    def get_input_desc(self) -> str:
        """
        入参的描述
        Returns: str, 入参的描述
        """

    @abstractmethod
    def get_output_desc(self) -> str:
        """
        返回值的描述
        Returns: str, 返回值的描述
        """
