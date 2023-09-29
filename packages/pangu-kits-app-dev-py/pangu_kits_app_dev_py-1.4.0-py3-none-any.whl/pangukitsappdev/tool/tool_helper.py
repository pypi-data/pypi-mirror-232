#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
from abc import ABC
from typing import Type
from pangukitsappdev.api.tool.base import Tool
from pangukitsappdev.prompt.prompt_tmpl import PromptTemplates
from pangukitsappdev.tool.tool_bo import ToolBo


class ToolHelper(ABC):
    """Tool辅助类
    """

    @staticmethod
    def get_tool_bo(tool: Tool) -> ToolBo:
        # 获取输入输出的类型
        input_type = tool.args_schema
        output_type = tool.output_type
        desc = tool.get_tool_desc() + ", " + tool.get_tool_principle()

        return ToolBo(name=tool.get_tool_name(),
                      desc=desc,
                      input_type=input_type,
                      output_type=output_type,
                      input_schema=ToolHelper.get_tool_schema(tool.get_input_desc(), input_type),
                      output_schema=ToolHelper.get_tool_schema(tool.get_output_desc(), output_type),
                      tool=tool)

    @staticmethod
    def get_tool_schema(desc: str, class_type: Type) -> str:

        # 基本类型直接返回
        if class_type in [int, float, str, bool]:
            return PromptTemplates.get("agent_tool_simple_schema").format(desc=desc,
                                                                          type=class_type.__name__)
        # 复杂类型返回JSON schema
        return PromptTemplates.get("agent_tool_json_schema"). \
            format(desc=desc,
                   schema={"properties": class_type.schema()["properties"]})
