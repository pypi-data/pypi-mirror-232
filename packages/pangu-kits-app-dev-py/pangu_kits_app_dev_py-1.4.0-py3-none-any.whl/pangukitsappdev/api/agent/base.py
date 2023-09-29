#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
from abc import ABC, abstractmethod
from pangukitsappdev.api.llms.base import LLMApi
from pangukitsappdev.api.tool.base import Tool
from pangukitsappdev.tool.tool_helper import ToolHelper


class Agent(ABC):

    @abstractmethod
    def add_tool(self, tool: Tool):
        """
        为Agent增加工具类
        :param tool: Tool
        """

    @abstractmethod
    def run(self, prompt: str) -> str:
        """
        执行agent
        :param prompt: 用户的输入
        :return: 计划的结果
        """


class AbstractAgent(Agent):
    def __init__(self, llm: LLMApi, max_iterations: int = 15):
        """
        构造一个agent
        :param llm: LLMApi
        """
        self.llm = llm
        self.tool_map = {}
        self.max_iterations = max_iterations

    def add_tool(self, tool: Tool):
        tool_name = tool.get_tool_name()
        if not tool_name or tool_name in self.tool_map.keys():
            raise ValueError("tool_name must not be empty or repeat")
        self.tool_map.update({tool.get_tool_name(): ToolHelper.get_tool_bo(tool)})

    @abstractmethod
    def run(self, prompt: str) -> str:
        """
        执行agent
        :param prompt: 用户的输入
        :return: 计划的结果
        """
