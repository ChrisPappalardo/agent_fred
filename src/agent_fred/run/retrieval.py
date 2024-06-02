import sys
from pprint import PrettyPrinter

from agent_fred.config import config
from agent_fred.core import xlsx_to_haystack_docs
from agent_fred.pipelines import retrieval_pipeline


if __name__ == "__main__":
    print("retrieval pipeline for q&a on a file using natural language")
    print(f"using {config.embedding_model} embeddings and {config.llm} llm")

    # get xlsx filename from user
    default_filename = "tests/test_data/GDPC1_1.xls"
    filename = input(f"load [{default_filename}]: ") or default_filename

    # parse tables from xlsx file and convert to haystack Documents
    documents = xlsx_to_haystack_docs(filename)

    if config.debug:
        PrettyPrinter().pprint(documents)

    # create pipeline
    pipeline = retrieval_pipeline(
        documents=documents,
        embedding_kwargs={"model": config.embedding_model},
    )

    # loop for q&a
    while True:
        try:
            question = input("Question: ")
            response = pipeline.run({"text_embedder": {"text": question}})
            PrettyPrinter().pprint(response["retriever"]["documents"])
        except KeyboardInterrupt:
            print("exiting...")
            sys.exit(0)
