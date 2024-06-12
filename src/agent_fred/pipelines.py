import re
from typing import Any

from haystack import Document, Pipeline
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import (
    InMemoryBM25Retriever,
    InMemoryEmbeddingRetriever,
)
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import (
    OllamaGenerator,
    OllamaChatGenerator,
)

from agent_fred.components import CustomConditionalRouter, FredCleaner, FredFetcher


# generic
# -----------------------------------------------------------------------------
def prompt_pipeline(
    prompt_template: str,
    llm_kwargs: dict[str, Any] = {},
) -> Pipeline:
    """create and return a single prompt to answer pipeline"""

    # initialize other components
    prompt_builder = PromptBuilder(template=prompt_template)
    generator = OllamaGenerator(**llm_kwargs)

    # create pipeline
    pipeline = Pipeline()
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", generator)
    pipeline.connect("prompt_builder", "llm")

    return pipeline


def retrieval_pipeline(
    documents: list[Document],
    embedding_kwargs: dict[str, Any] = {},
) -> Pipeline:
    """create and return retrieval pipeline"""

    # store documents with embeddings
    document_store = InMemoryDocumentStore()
    document_embedder = OllamaDocumentEmbedder(**embedding_kwargs)
    docs_with_embeddings = document_embedder.run(documents)["documents"]
    document_store.write_documents(docs_with_embeddings)

    # initialize other haystack components
    text_embedder = OllamaTextEmbedder(**embedding_kwargs)
    retriever = InMemoryEmbeddingRetriever(document_store=document_store)

    # create pipeline
    pipeline = Pipeline()
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("retriever", retriever)
    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

    return pipeline


def rag_pipeline(
    documents: list[Document],
    prompt_template: str,
    embedding_kwargs: dict[str, Any] = {},
    llm_kwargs: dict[str, Any] = {},
) -> Pipeline:
    """create and return rag pipeline"""

    # create retrieval pipeline
    pipeline = retrieval_pipeline(
        documents=documents,
        embedding_kwargs=embedding_kwargs,
    )

    # initialize other haystack components
    prompt_builder = PromptBuilder(template=prompt_template)
    generator = OllamaGenerator(**llm_kwargs)

    # create pipeline
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", generator)
    pipeline.connect("retriever", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")

    return pipeline


# fred
# -----------------------------------------------------------------------------
def fred_agent_pipeline(
    prompt_template: str,
    api_key: str,
    llm_kwargs: dict[str, Any] = {},
) -> Pipeline:
    """create and return fred agent pipeline"""

    def my_func(value: str):
        """extract args for fred fetcher"""
        patt = r'my_func\("(.*?)",\s?"(.*?)",\s?"(.*?)"\)'
        match = re.search(patt, value, re.DOTALL)
        if match:
            keys = ("series_id", "start_date", "end_date")
            return dict(zip(keys, match.groups()))
        return None

    routes = [
        {
            "condition": "{{ replies[0]|custom_filter != None }}",
            "output": "{{ replies[0]|custom_filter }}",
            "output_name": "agent_reply",
            "output_type": dict,
        },
        {
            "condition": "{{ replies[0]|custom_filter == None }}",
            "output": "{{ question }}",
            "output_name": "fallback_reply",
            "output_type": str,
        },
    ]

    # initialize components
    router = CustomConditionalRouter(custom_filter=my_func, routes=routes)
    fetcher = FredFetcher(api_key=Secret.from_token(api_key))
    cleaner = FredCleaner()

    # create pipeline
    pipeline = prompt_pipeline(
        prompt_template=prompt_template,
        llm_kwargs=llm_kwargs,
    )
    pipeline.add_component("router", router)
    pipeline.add_component("fetcher", fetcher)
    pipeline.add_component("cleaner", cleaner)
    pipeline.connect("llm.replies", "router")
    pipeline.connect("router.agent_reply", "fetcher")
    pipeline.connect("fetcher", "cleaner")

    return pipeline


def fred_chat_pipeline(
    agent_prompt_template: str,
    chat_prompt_template: str,
    api_key: str,
    agent_llm_kwargs: dict[str, Any] = {},
    chat_llm_kwargs: dict[str, Any] = {},
) -> tuple[Pipeline, InMemoryDocumentStore]:
    """create and return fred chat pipeline and document store"""

    chat_prompt_builder_template = [
        ChatMessage.from_system(
            """You are an expert economics assistant that provides helpful
            answers to questions about economics. Keep your answers brief
            and factual, do not make anything up."""
        ),
        ChatMessage.from_user(chat_prompt_template),
    ]

    # initialize haystack components
    document_store = InMemoryDocumentStore()
    retriever = InMemoryBM25Retriever(document_store=document_store)
    chat_prompt_builder = ChatPromptBuilder(
        template=chat_prompt_builder_template,
        variables=["documents"],
    )
    chat_generator = OllamaChatGenerator(**chat_llm_kwargs)

    # create pipeline
    pipeline = fred_agent_pipeline(
        prompt_template=agent_prompt_template,
        api_key=api_key,
        llm_kwargs=agent_llm_kwargs,
    )
    pipeline.add_component("retriever", retriever)
    pipeline.add_component("chat_prompt_builder", chat_prompt_builder)
    pipeline.add_component("chat_llm", chat_generator)
    pipeline.connect("router.fallback_reply", "retriever")
    pipeline.connect("retriever", "chat_prompt_builder.documents")
    pipeline.connect("chat_prompt_builder.prompt", "chat_llm.messages")

    return pipeline, document_store
