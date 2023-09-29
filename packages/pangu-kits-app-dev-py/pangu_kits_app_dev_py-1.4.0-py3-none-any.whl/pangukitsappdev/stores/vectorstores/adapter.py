#  Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.

from langchain.vectorstores import VectorStore

from pangukitsappdev.api.store.vector.base import AbstractVectorApi
from pangukitsappdev.api.store.vector.vector_config import VectorStoreConfig
from pangukitsappdev.stores.vectorstores.css_store import CSSVectorSearch


class CSSVectorApi(AbstractVectorApi):
    def create_vector_store(self, vector_config: VectorStoreConfig) -> VectorStore:
        config = {
            "elasticsearch_url": vector_config.server_info.get_urls(),
            "index_name": vector_config.index_name,
            "embedding": vector_config.embedding,
            "verify_certs": vector_config.verify_certs,
            "proxies": vector_config.http_config.requests_proxies()
        }

        return CSSVectorSearch(**config)

    def clear(self):
        if not self.vector_store.client.indices.exists(self.vector_store.index_name):
            return
        self.vector_store.client.indices.delete(index=self.vector_store.index_name)
