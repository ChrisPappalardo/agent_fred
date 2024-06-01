from typing import Any

from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaGenerator


def rag_pipeline(
    documents: list[Document],
    prompt_template: str,
    embedding_kwargs: dict[str, Any] = {},
    llm_kwargs: dict[str, Any] = {},
) -> Pipeline:
    """create and return rag pipeline"""
    # store documents with embeddings
    document_store = InMemoryDocumentStore()
    document_embedder = OllamaDocumentEmbedder(**embedding_kwargs)
    docs_with_embeddings = document_embedder.run(documents)["documents"]
    document_store.write_documents(docs_with_embeddings)

    # initialize other haystack components
    text_embedder = OllamaTextEmbedder(**embedding_kwargs)
    retriever = InMemoryEmbeddingRetriever(document_store=document_store)
    prompt_builder = PromptBuilder(template=prompt_template)
    generator = OllamaGenerator(**llm_kwargs)

    # create pipeline
    pipeline = Pipeline()
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("retriever", retriever)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", generator)
    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    pipeline.connect("retriever", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")

    return pipeline
