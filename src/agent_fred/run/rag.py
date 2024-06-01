import logging
import os
from pprint import PrettyPrinter

from agent_fred.core import load_prompt, xlsx_to_haystack_docs
from agent_fred.pipelines import rag_pipeline

debug = os.environ.get("RAG_DEBUG", False)
prompt_filename = os.environ.get("RAG_PROMPT", "src/agent_fred/prompts/rag.txt")
embedding_model = os.environ.get("RAG_EMBEDDINGS", "phi3")
llm = os.environ.get("RAG_LLM", "phi3")
temperature = os.environ.get("RAG_TEMPERATURE", 0.0)

if debug:
    logging.basicConfig(
        format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
    )
    logging.getLogger("haystack").setLevel(logging.INFO)


if __name__ == "__main__":
    print(f"using {embedding_model} for embeddings and {llm} for chat")

    # get xlsx filename from user
    default_filename = "tests/test_data/GDPC1_1.xls"
    filename = input(f"load [{default_filename}]: ") or default_filename

    # parse tables from xlsx file and convert to haystack Documents
    documents = xlsx_to_haystack_docs(filename)

    if debug:
        PrettyPrinter().pprint(documents)

    # create pipeline
    pipeline = rag_pipeline(
        documents=documents,
        prompt_template=load_prompt(prompt_filename),
        embedding_kwargs={"model": embedding_model},
        llm_kwargs={
            "model": llm,
            "generation_kwargs": {"temperature": float(temperature)},
        },
    )

    # loop for q&a
    while True:
        question = input("Question: ")
        response = pipeline.run(
            {
                "prompt_builder": {"question": question},
                "text_embedder": {"text": question},
            }
        )
        print(response["llm"]["replies"][0])
