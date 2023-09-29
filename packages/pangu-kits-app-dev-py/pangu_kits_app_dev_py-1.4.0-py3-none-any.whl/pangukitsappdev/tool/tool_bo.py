#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
from typing import Type
from pydantic import BaseModel
from pangukitsappdev.api.tool.base import Tool


class ToolBo(BaseModel):
    """
    工具实体的定义
    Attributes:
        name: 工具名称
        desc: 工具描述
        input_type: 工具输入类型
        output_type: 工具输出类型
        input_schema: 工具输入Schema
        output_schema: 工具输出Schema
        tool: 工具
    """
    name: str
    desc: str
    input_type: Type
    output_type: Type
    input_schema: str
    output_schema: str
    tool: Tool
