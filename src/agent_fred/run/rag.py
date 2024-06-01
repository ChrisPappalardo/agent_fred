import logging
import os

from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaGenerator

from agent_fred.core import load_prompt, xlsx_to_haystack_docs


if os.environ.get("RAG_DEBUG", None) is not None:
    logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
    logging.getLogger("haystack").setLevel(logging.INFO)

prompt_filename = os.environ.get("RAG_PROMPT", "src/agent_fred/rag_prompt.txt")


if __name__ == "__main__":
    print("[rag pipeline]")

    # get xlsx filename from user
    filename = input("load path/filename.xlsx: ")

    # parse tables from xlsx file and convert to haystack Documents
    documents = xlsx_to_haystack_docs(filename)

    # create prompt
    prompt_template = load_prompt(prompt_filename)

    # store documents with embeddings
    document_store = InMemoryDocumentStore()
    document_embedder = OllamaDocumentEmbedder(model="phi3")  # for docs
    docs_with_embeddings = document_embedder.run(documents)["documents"]
    document_store.write_documents(docs_with_embeddings)

    # initialize other haystack components
    text_embedder = OllamaTextEmbedder(model="phi3")  # for query
    retriever = InMemoryEmbeddingRetriever(document_store=document_store)
    prompt_builder = PromptBuilder(template=prompt_template)
    generator = OllamaGenerator(
        model="phi3", generation_kwargs={"temperature": 0.0},
    )

    # create pipeline
    pipeline = Pipeline()
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("retriever", retriever)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", generator)
    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    pipeline.connect("retriever", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")

    # loop for q&a
    while True:
        question = input("Question: ")
        response = pipeline.run({
            "prompt_builder": {"question": question},
            "text_embedder": {"text": question},
        })
        print(response["llm"]["replies"][0])
