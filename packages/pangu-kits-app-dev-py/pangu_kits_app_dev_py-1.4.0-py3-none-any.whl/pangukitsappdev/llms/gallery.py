#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
import json
import logging
from json import JSONDecodeError
from typing import List, Optional, Iterator, Any

import requests
import sseclient
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema.output import GenerationChunk, LLMResult, Generation
from pydantic import Field
from requests.exceptions import ChunkedEncodingError

from pangukitsappdev.api.llms.base import AbstractLLMApi
from pangukitsappdev.api.llms.llm_config import LLMConfig
from pangukitsappdev.auth.iam import IAMTokenProvider, IAMTokenProviderFactory
from pangukitsappdev.llms.response.llm_response_gallery import LLMRespGallery
from pangukitsappdev.llms.response.gallery_text_resp import GalleryUsage, GalleryTextResp, GalleryTextChoice
from pangukitsappdev.api.common_config import AUTH_TOKEN_HEADER

logger = logging.getLogger(__name__)


class GalleryLLM(LLM):
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    gallery_url: str
    token_getter: IAMTokenProvider
    streaming: bool = False
    proxies: dict = {}
    prefix_messages: List = Field(default_factory=list)

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        llm_result = self._generate([prompt], stop, run_manager)
        return llm_result.generations[0][0].text

    @property
    def _llm_type(self) -> str:
        return "gallery_llm"

    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        request_body = {
            "prompt": prompt,
            "stream": True,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "history": [f"{prefix_message.get('role')}:{prefix_message.get('content')}"
                        for prefix_message in self.prefix_messages]
        }
        token = self.token_getter.get_valid_token()
        headers = {
            AUTH_TOKEN_HEADER: token
        } if token else {}
        rsp = requests.post(self.gallery_url, headers=headers,
                            json=request_body,
                            verify=False, stream=True, proxies=self.proxies)
        try:
            rsp.raise_for_status()
            stream_client: sseclient.SSEClient = sseclient.SSEClient(rsp)
            for event in stream_client.events():
                # 解析出Token数据
                data_json = json.loads(event.data)
                chunk = GenerationChunk(text=data_json["choices"][0]["text"])
                yield chunk
                if run_manager:
                    run_manager.on_llm_new_token(chunk.text)
        except JSONDecodeError as ex:
            """[DONE]表示stream结束了"""
            if event.data != "[DONE]":
                logger.warning(f"Meet json decode error: {str(ex)}")
        except ChunkedEncodingError as ex:
            logger.warning(f"Meet error: {str(ex)}")

    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompt and input."""
        generations = []
        llm_output = {}
        for prompt in prompts:
            request_body = {
                "prompt": prompt,
                "stream": self.streaming,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "history": [f"{prefix_message.get('role')}:{prefix_message.get('content')}"
                            for prefix_message in self.prefix_messages]
            }
            token = self.token_getter.get_valid_token()
            headers = {
                AUTH_TOKEN_HEADER: token
            } if token else {}
            rsp = requests.post(self.gallery_url, headers=headers,
                                json=request_body,
                                verify=False, stream=self.streaming, proxies=self.proxies)

            if 200 == rsp.status_code:
                llm_output = rsp.json()
                text = llm_output["choices"][0]["text"]
                generations.append([Generation(text=text)])
            else:
                logger.error("Call pangu llm failed, http status: %d, error response: %s", rsp.status_code, rsp.content)
                rsp.raise_for_status()

        return LLMResult(generations=generations, llm_output=llm_output)


class GalleryLLMApi(AbstractLLMApi):

    def do_create_llm(self, llm_config: LLMConfig):
        config_kwargs = {
            "gallery_url": llm_config.gallery_config.gallery_url,
            "token_getter": IAMTokenProviderFactory.create(llm_config.gallery_config.iam_config),
            "proxies": llm_config.gallery_config.http_config.requests_proxies()
        }
        llm_param_config_dict: dict = llm_config.llm_param_config.dict(exclude_none=True, exclude={"stream"})
        if llm_config.llm_param_config.stream:
            llm_param_config_dict["streaming"] = llm_config.llm_param_config.stream
        config_kwargs = {**config_kwargs, **llm_param_config_dict}
        return GalleryLLM(**config_kwargs)

    def parse_llm_response(self, llm_result: LLMResult) -> LLMRespGallery:
        answer = llm_result.generations[0][0].text
        llm_output = llm_result.llm_output
        choices = [GalleryTextChoice(index=choice["index"],
                                     text=choice["text"]) for choice in llm_output.get("choices")]
        if llm_output.get("usage") is not None:
            usage = GalleryUsage(completion_tokens=llm_output.get("usage").get("completion_tokens"),
                                 prompt_tokens=llm_output.get("usage").get("prompt_tokens"),
                                 total_tokens=llm_output.get("usage").get("total_tokens"))
        else:
            usage = None

        llm_resp = LLMRespGallery(answer=answer,
                                  is_from_cache=False,
                                  gallery_text_resp=GalleryTextResp(id=llm_output.get("id"),
                                                                    created=llm_output.get("created"),
                                                                    choices=choices,
                                                                    usage=usage))
        return llm_resp
