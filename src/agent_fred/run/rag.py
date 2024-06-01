import logging
import os
from pprint import PrettyPrinter

from agent_fred.core import load_prompt, xlsx_to_haystack_docs
from agent_fred.pipelines import rag_pipeline


if debug := os.environ.get("RAG_DEBUG", None) is not None:
    logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
    logging.getLogger("haystack").setLevel(logging.INFO)

prompt_filename = os.environ.get("RAG_PROMPT", "src/agent_fred/prompts/rag.txt")


if __name__ == "__main__":
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
        embedding_kwargs={"model": "phi3"},
        llm_kwargs={
            "model": "phi3",
            "generation_kwargs": {"temperature": 0.0},
        },
    )

    # loop for q&a
    while True:
        question = input("Question: ")
        response = pipeline.run({
            "prompt_builder": {"question": question},
            "text_embedder": {"text": question},
        })
        print(response["llm"]["replies"][0])
