from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore

from agent_fred.pipelines import (
    prompt_pipeline,
    retrieval_pipeline,
    rag_pipeline,
    fred_agent_pipeline,
    fred_chat_pipeline,
)


def test_prompt_pipeline() -> None:
    """test that prompt pipeline can be instantiated"""
    prompt_template = "test {{ question }}"
    pipeline = prompt_pipeline(prompt_template=prompt_template)
    assert isinstance(pipeline, Pipeline)


def test_retrieval_pipeline() -> None:
    """test that retrieval pipeline can be instantiated"""
    documents = []
    pipeline = retrieval_pipeline(documents=documents)
    assert isinstance(pipeline, Pipeline)


def test_rag_pipeline() -> None:
    """test that rag pipeline can be instantiated"""
    documents = []
    prompt_template = "test {{ documents }} {{ question }}"
    pipeline = rag_pipeline(documents=documents, prompt_template=prompt_template)
    assert isinstance(pipeline, Pipeline)


def test_fred_agent_pipeline() -> None:
    """test that fred agent pipeline can be instantiated"""
    prompt_template = "test {{ question }}"
    pipeline = fred_agent_pipeline(prompt_template=prompt_template, api_key="123")
    assert isinstance(pipeline, Pipeline)


def test_fred_chat_pipeline() -> None:
    """test that fred chat pipeline can be instantiated"""
    agent_prompt_template = "test {{ question }}"
    chat_prompt_template = "test {{ documents }}{{ question }}"
    pipeline, document_store = fred_chat_pipeline(
        agent_prompt_template=agent_prompt_template,
        chat_prompt_template=chat_prompt_template,
        api_key="123",
    )
    assert isinstance(pipeline, Pipeline)
    assert isinstance(document_store, InMemoryDocumentStore)
