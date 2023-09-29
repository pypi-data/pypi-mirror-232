#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
import json
import logging
from abc import ABC, abstractmethod
from typing import Iterator, Type, List, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult, BaseMessage, ChatMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel

from pangukitsappdev.api.llms.llm_config import LLMParamConfig, LLMConfig
from pangukitsappdev.api.schema import LLMResp
from pangukitsappdev.api.store.cache.base import CacheApi
from pangukitsappdev.prompt.prompt_tmpl import PromptTemplates

logger = logging.getLogger(__name__)


class LLMApi(ABC):

    @abstractmethod
    def ask(self,
            prompt: str,
            param_config: LLMParamConfig = None,
            prefix_messages: List[BaseMessage] = None) -> Union[LLMResp, Iterator]:
        """
        问答
        :param prompt: 提示词
        :param param_config: (Optional)覆盖llm的原本的参数配置，用来控制llm的返回信息
        :param prefix_messages: (Optional)多轮对话
        :return: LLMResp or Iterator(流式打印)
        """

    @abstractmethod
    def set_cache(self, cache: CacheApi):
        """
        设置缓存
        :param cache: 缓存实现对象
        :return: void
        """

    @abstractmethod
    def set_callback(self, callback: BaseCallbackHandler):
        """
        设置Callback回调对象
        :param callback: callback对象
        """

    @abstractmethod
    def ask_for_object(self, prompt: str, class_type: Type[BaseModel], param_config: LLMParamConfig = None):
        """
        问答
        :param prompt: 提示词
        :param class_type: 需要LLM转换的类型
        :param param_config: (Optional)覆盖llm的原本的参数配置，用来控制llm的返回信息
        :return: LLM answer
        """


class AbstractLLMApi(LLMApi):

    @staticmethod
    def _build_llm_string(llm: BaseLLM) -> str:
        return str(sorted([(k, v) for k, v in llm.dict().items()]))

    @staticmethod
    def _parse_llm_response(llm_result: LLMResult) -> LLMResp:
        answer_generation = llm_result.generations[0][0]
        answer = answer_generation.text
        llm_resp = LLMResp(answer=answer, is_from_cache=False)
        return llm_resp

    def __init__(self, llm_config: LLMConfig, llm: BaseLLM = None, cache: CacheApi = None):
        """ 构造器

          Args:
              llm_config: 通过构造器传递的LLM参数
              llm: （Optional）内部封装的Langchain BaseLLM的实现类
              cache: CacheApi的实现类，为LLM增加缓存
        """
        self.llm_config = llm_config
        self.llm = llm if llm else self.create_llm_with()

        self.callback_handler = None
        self.cache = cache

    def ask(self,
            prompt: str,
            param_config: LLMParamConfig = None,
            prefix_messages: List[BaseMessage] = None) -> Union[LLMResp, Iterator]:
        # 根据入参LLMParamConfig判断是否是流式打印，返回类型为Iterator[str]
        if param_config and param_config.stream:
            return self._stream(prompt=prompt, param_config=param_config, prefix_messages=prefix_messages)

        # 根据构造器传递的LLMConfig中的LLMParamConfig判断是否是流式打印
        if self.llm_config and self.llm_config.llm_param_config and self.llm_config.llm_param_config.stream:
            return self._stream(prompt=prompt, prefix_messages=prefix_messages)

        # 非流式打印返回类型为LLMResp
        local_llm = self.llm if param_config is None else self.create_llm_with(param_config)

        # 尝试从缓存获取响应
        if self.cache:
            """移除session_tag的构造，session_tag在cache初始化时传入，不在lookup中传递
            """
            cached_llm_rsp = self.cache.lookup(prompt=prompt)
            if cached_llm_rsp:
                """这里需要复制所有的成员变量，当前只有answer和is_from_cache"""
                logger.debug("Hit cached completion. prompt: %s", prompt)
                return LLMResp(answer=cached_llm_rsp.answer, is_from_cache=True)

            logger.debug("Miss cache")

        llm_result: LLMResult = local_llm.generate([prompt],
                                                   callbacks=[self.callback_handler] if self.callback_handler else None)

        llm_resp = self.parse_llm_response(llm_result)

        # 尝试更新缓存
        if self.cache and not llm_resp.is_from_cache:
            self.cache.update(prompt=prompt,
                              value=llm_resp)
            logger.debug("Update cache for prompt %s", prompt)

        return llm_resp

    def ask_for_object(self, prompt: str, class_type: Type[BaseModel], param_config: LLMParamConfig = None):
        final_prompt = PromptTemplates.get("system_out_put_parser").format(schema=dict(
            properties=class_type.schema()["properties"]), prompt=prompt)
        llm_resp = self.ask(final_prompt, param_config)

        # 流式打印拼凑结果后输出
        if isinstance(llm_resp, Iterator):
            actual_tokens = []
            for token in llm_resp:
                actual_tokens.append(token)
            answer = "".join(actual_tokens)
        else:
            answer = llm_resp.answer
        return class_type(**json.loads(answer))

    def set_cache(self, cache: CacheApi):
        self.cache = cache

    def default_create_llm_func(self, param_config: LLMParamConfig) -> BaseLLM:
        """创建llm的默认方法
        使用llm的类直接构造，调用这个默认实现是self.llm必须存在
        使用param_config构造新的llm
        :param param_config: llm参数配置
        :return: 使用新参数构造的llm
        """
        if not self.llm:
            raise ValueError("the default create llm func need preset a BaseLLM instance")
        llm_type = type(self.llm)
        return llm_type(**param_config.dict())

    def set_callback(self, callback: BaseCallbackHandler):
        self.callback_handler = callback

    def _stream(self,
                prompt: str,
                param_config: LLMParamConfig = None,
                prefix_messages: List[BaseMessage] = None) -> Iterator[str]:
        local_llm = self.llm if param_config is None else self.create_llm_with(param_config)
        # 尝试从缓存获取响应
        if self.cache:
            """缓存命中，直接从缓存中读取，返回size为1的迭代器
            """
            cached_llm_rsp = self.cache.lookup(prompt=prompt)
            if cached_llm_rsp:
                """返回命中cache"""
                logger.debug("Hit cached completion. prompt: %s", prompt)
                yield cached_llm_rsp.answer
                return
            logger.debug("Miss cache")
        # 通过stream方式获取response

        tokens = local_llm.stream(prompt,
                                  config=dict(callbacks=[self.callback_handler]) if self.callback_handler else None)

        answer = ""
        for token in tokens:
            yield token
            answer += token
        llm_resp = LLMResp(answer=answer, is_from_cache=False)

        # 尝试更新缓存
        if self.cache and not llm_resp.is_from_cache:
            self.cache.update(prompt=prompt,
                              value=llm_resp)
            logger.debug("Update cache for prompt %s", prompt)

    def do_create_llm(self, llm_config: LLMConfig):
        return self.default_create_llm_func(llm_config.llm_param_config)

    def create_llm_with(self, param_config: LLMParamConfig = None) -> BaseLLM:
        if param_config:
            llm_config: LLMConfig = self.llm_config.copy(deep=True)
            llm_config.llm_param_config = param_config
            return self.do_create_llm(llm_config)
        else:
            return self.do_create_llm(self.llm_config)

    def parse_llm_response(self, llm_result: LLMResult) -> LLMResp:
        return self._parse_llm_response(llm_result)

    @staticmethod
    def to_message_in_req(message: BaseMessage) -> dict:
        """
        将message转换成请求体，当前只识别system的role，其他的message按照顺序组装，依次是user，assistant
        :param message: 回复或请求的问题
        :return: 消息体中的dict数据
        """
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "assistant", "content": message.content}
        elif isinstance(message, SystemMessage):
            message_dict = {"role": "system", "content": message.content}
        else:
            raise ValueError(f"Got unknown type {message}")

        return message_dict


class LLMApiAdapter(AbstractLLMApi):
    """LLMApi的适配器
    负责把Langchain的LLM实现类适配到LLMApiAdapter

    Attributes:
        llm: 内部封装的Langchain BaseLLM的实现类
    """

    def __init__(self, llm: BaseLLM):
        llm_config = LLMConfig()
        super().__init__(llm_config, llm)
