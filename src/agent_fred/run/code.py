import sys
from pprint import PrettyPrinter

from eparse.core import get_df_from_file

from agent_fred.config import config
from agent_fred.core import load_prompt
from agent_fred.pipelines import prompt_pipeline


if __name__ == "__main__":
    print("retrieval pipeline for search on a file using natural language")
    print(f"using {config.embedding_model} embeddings and {config.llm} llm")

    # get xlsx filename from user
    default_filename = "tests/test_data/GDPC1_1.xls"
    filename = input(f"load [{default_filename}]: ") or default_filename

    # extract sub-tables from xlsx
    dfs = list(get_df_from_file(filename))

    if config.debug:
        PrettyPrinter().pprint(dfs)

    # create pipeline
    pipeline = prompt_pipeline(
        prompt_template=load_prompt("src/agent_fred/prompts/code.txt"),
        llm_kwargs={
            "model": config.llm,
            "generation_kwargs": {"temperature": float(config.temperature)},
        },
    )

    # run prompt on each sub-table
    while True:
        try:
            question = input("Question: ")

            for df in dfs:
                response = pipeline.run(
                    {"prompt_builder": {"table": df[0], "question": question}},
                )
                print(response["llm"]["replies"][0])
        except KeyboardInterrupt:
            print("exiting...")
            sys.exit(0)
