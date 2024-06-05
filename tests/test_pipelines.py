from haystack import Pipeline

from agent_fred.pipelines import (
    prompt_pipeline,
    retrieval_pipeline,
    rag_pipeline,
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
