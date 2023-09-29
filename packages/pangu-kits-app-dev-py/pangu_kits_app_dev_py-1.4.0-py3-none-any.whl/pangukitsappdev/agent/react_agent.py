#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
import json
import logging
from json import JSONDecodeError
from typing import List
from pydantic import ValidationError
from pangukitsappdev.agent.action_bo import ActionBo
from pangukitsappdev.api.agent.base import AbstractAgent
from pangukitsappdev.api.llms.base import LLMApi
from pangukitsappdev.prompt.prompt_tmpl import PromptTemplates

logger = logging.getLogger(__name__)


class ReactAgent(AbstractAgent):
    PLACEHOLDER_THOUGHT = "Thought:"
    PLACEHOLDER_ACTION = "Action:"
    PLACEHOLDER_OBSERVATION = "Observation:"
    FINAL_ACTION = "FINAL_ANSWER"

    def __init__(self, llm: LLMApi, max_iterations: int = 15):
        super(ReactAgent, self).__init__(llm, max_iterations)

    def run(self, prompt: str) -> str:
        if not prompt:
            raise ValueError("prompt should not be empty!")

        actions: List[ActionBo] = []
        try:
            self.react(prompt, actions)
        except (ValueError, JSONDecodeError, TypeError) as e:
            logger.debug("run error when call react", e)
            self.print_plan(actions)
            raise e
        self.print_plan(actions)
        return str(actions[-1].action_input)

    def react(self, prompt: str, actions: List[ActionBo]):
        # 超过最大迭代次数限制，不再执行
        if len(actions) >= self.max_iterations:
            logger.debug("stopped due to iteration limit. maxIterations is %s", self.max_iterations)
            raise ValueError("stopped due to iteration limit.")

        # 构造React prompt
        react_tp = PromptTemplates.get("agent_react")
        final_prompt = react_tp.format(tool_desc=self.get_tool_desc(),
                                       tool_names=self.get_tool_names(),
                                       prompt=prompt,
                                       actions=[{"thought": action.thought,
                                                 "actionJson": action.action_json,
                                                 "action": action.action,
                                                 "observation": action.observation} for action in actions])

        # 获取action
        action = self.get_action(self.llm.ask(final_prompt).answer)
        actions.append(action)

        # 如果没有结束，执行action
        if not self.is_final(action):
            # 查询tool
            tool_bo = self.tool_map.get(action.action)
            if tool_bo is None:
                logger.debug("can not find tool for %s in %s", action.action, str(self.tool_map.keys()))
                raise ValueError("agent did not return a valid action")

            # 执行tool
            tool = tool_bo.tool
            try:
                tool_input = tool_bo.input_type.parse_obj(action.action_input)
            except ValidationError:
                logger.debug("agent did not return a valid tool input, input=%s, but tool need %s",
                             action.action_input, tool_bo.input_type)
                raise ValueError("agent did not return a valid tool input")

            tool_result = tool.run(tool_input.dict())

            if isinstance(tool_result, (str, int, float, bool)):
                action.observation = str(tool_result)
            else:
                action.observation = tool_result.json()
            logger.info("actions = %s", "\n".join([action.json() for action in actions]))
            self.react(prompt, actions)

    def is_final(self, action: ActionBo) -> bool:
        return action.action == self.FINAL_ACTION

    def get_action(self, answer: str) -> ActionBo:
        # 获取第一个action
        action_str = self.sub_str_between(answer, self.PLACEHOLDER_ACTION, self.PLACEHOLDER_OBSERVATION)
        action_bo = self.get_action_bo(action_str)
        action_bo.thought = self.sub_str_between(answer, self.PLACEHOLDER_THOUGHT, self.PLACEHOLDER_ACTION)

        return action_bo

    @staticmethod
    def sub_str_between(origin_str: str, start_str: str, end_str: str):
        start_pos = origin_str.find(start_str)
        start_pos = start_pos + len(start_str) if start_pos != -1 else 0
        end_pos = origin_str.find(end_str)
        end_pos = end_pos if end_pos != -1 else len(origin_str)
        if start_pos > end_pos:
            final_str = origin_str[:end_pos]
        else:
            final_str = origin_str[start_pos:end_pos]
        return final_str

    @staticmethod
    def get_action_bo(action_str: str) -> ActionBo:
        try:
            action_json = action_str
            action_bo = ActionBo(**json.loads(action_json.replace("actionInput", "action_input")))
        except (JSONDecodeError, TypeError):
            logger.debug("try to load json failed, json:%s", action_json)
            # 尝试通过工程修复一些LLM返回的错误JSON，修正中文逗号
            fix_str = action_str.replace("，", ",")
            try:
                action_json = fix_str
                action_bo = ActionBo(**json.loads(action_json.replace("actionInput", "action_input")))
            except (JSONDecodeError, TypeError):
                logger.debug("After replace the comma, try to load json failed, json:%s", action_json)
                # 查询一个完整的{}，忽略字符串中的{}(简化)
                first_pos = fix_str.find("{")
                if first_pos < 0 or len(fix_str) < 2:
                    raise ValueError("try to fix json failed, agent did not return a valid action")
                match_count = 1
                last_pos = first_pos + 1
                while last_pos < len(fix_str):
                    if fix_str[last_pos] == "{":
                        match_count += 1
                    if fix_str[last_pos] == "}":
                        match_count -= 1
                    if match_count == 0:
                        break
                    last_pos += 1
                try:
                    action_json = fix_str[first_pos: last_pos + 1]
                    action_bo = ActionBo(**json.loads(action_json.replace("actionInput", "action_input")))
                except (JSONDecodeError, TypeError):
                    logger.debug("After fixed json, try to load json failed, json:%s", action_json)
                    raise ValueError("After fixed json, try to load json failed, json:" + action_json)
        action_bo.action_json = action_json
        return action_bo

    def get_tool_desc(self) -> str:
        return PromptTemplates.get("agent_tool_desc").format(tools=[{"name": tool.name,
                                                                     "desc": tool.desc,
                                                                     "inputSchema": tool.input_schema,
                                                                     "outputSchema": tool.output_schema}
                                                                    for tool in self.tool_map.values()])

    def get_tool_names(self) -> str:
        return ", ".join(self.tool_map.keys()) + ", " + self.FINAL_ACTION

    def print_plan(self, actions: List[ActionBo]):
        log_msg = "\n计划已执行完成,自动编排步骤:"
        for i, action in enumerate(actions):
            thought = action.thought.replace("\n", "")
            log_msg += f"\n步骤{i + 1}:\n思考:{thought}"
            if self.is_final(action):
                log_msg += "\n问题已求解:"
            else:
                log_msg += f"\n行动:使用工具[{action.action}],传入参数{action.action_input}\n工具返回:{action.observation}"
        logger.info(log_msg)
