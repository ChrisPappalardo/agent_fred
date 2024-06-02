from haystack import Pipeline

from agent_fred.pipelines import rag_pipeline


def test_rag_pipeline() -> None:
    """test that rag pipeline can be instantiated"""
    documents = []
    prompt_template = "test {{ documents }} {{ question }}"
    pipeline = rag_pipeline(documents=documents, prompt_template=prompt_template)
    assert isinstance(pipeline, Pipeline)
