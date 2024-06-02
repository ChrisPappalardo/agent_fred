from pprint import PrettyPrinter

from agent_fred.config import config
from agent_fred.core import load_prompt, xlsx_to_haystack_docs
from agent_fred.pipelines import rag_pipeline


if __name__ == "__main__":
    print(f"using {config.embedding_model} for embeddings and {config.llm} for chat")

    # get xlsx filename from user
    default_filename = "tests/test_data/GDPC1_1.xls"
    filename = input(f"load [{default_filename}]: ") or default_filename

    # parse tables from xlsx file and convert to haystack Documents
    documents = xlsx_to_haystack_docs(filename)

    if config.debug:
        PrettyPrinter().pprint(documents)

    # create pipeline
    pipeline = rag_pipeline(
        documents=documents,
        prompt_template=load_prompt(config.prompt_filename),
        embedding_kwargs={"model": config.embedding_model},
        llm_kwargs={
            "model": config.llm,
            "generation_kwargs": {"temperature": float(config.temperature)},
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
