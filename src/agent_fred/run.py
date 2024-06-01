import logging
import os

from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaGenerator

from agent_fred.core import xlsx_to_haystack_docs


if os.environ.get("DEBUG", None) is not None:
    logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
    logging.getLogger("haystack").setLevel(logging.INFO)


if __name__ == "__main__":
    # get xlsx filename from user
    filename = input("load path/filename.xlsx: ")

    # parse tables from xlsx file and convert to haystack Documents
    documents = xlsx_to_haystack_docs(filename)

    # create prompt
    prompt_template = """
You are a data analyst helping your manager answer some questions
using tables contained in a spreadsheet.  The tables have been converted
into sentences where each sentence corresponds to a cell in a table.
The sentences have the following format:
<column heading> and <row heading> is <value of the cell>

Your manager has provided you with the following table sentences:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

Your manager has asked you to answer the following question based on
the sentences provided.  Be brief in your response and stick to the
data contained in the table sentences.  Do not make things up and do
not elaborate on anything irrelevant to the question.
Question:  {{ question }}
Answer:
"""

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
        # result = pipeline.run({"text_embedder": {"text": question}})
        response = pipeline.run({
            "prompt_builder": {"question": question},
            "text_embedder": {"text": question},
        })
        print(response["llm"]["replies"][0])
