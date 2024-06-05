import re
import sys
from pprint import PrettyPrinter

from eparse.core import get_df_from_file

from agent_fred.config import config
from agent_fred.core import load_prompt
from agent_fred.pipelines import prompt_pipeline


if __name__ == "__main__":
    print("code interpreter pipeline for q&a on an excel table using nlp")
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
                # set up table
                table = df[0][1:]
                table.columns = df[0].iloc[0]
                table.set_index(table.columns[0], inplace=True)

                if config.debug:
                    PrettyPrinter().pprint(table)

                response = pipeline.run(
                    {"prompt_builder": {"table": table, "question": question}},
                )
                code = response["llm"]["replies"][0]
                print(code)

                if input("Run [n]? "):
                    match = re.search("```python(.*)```", code, re.DOTALL)
                    code = match.group(1) if match else code
                    exec(code, {"table": table})

        except KeyboardInterrupt:
            print("exiting...")
            sys.exit(0)
