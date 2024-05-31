import sys

from agent_fred.config import config
from agent_fred.core import load_prompt
from agent_fred.pipelines import fred_agent_pipeline


if __name__ == "__main__":
    print("agent pipeline for q&a on fred api using nlp")
    print(f"using {config.embedding_model} embeddings and {config.llm} llm")

    # create pipeline
    pipeline = fred_agent_pipeline(
        prompt_template=load_prompt("src/agent_fred/prompts/agent.txt"),
        api_key=config.fred_api_key,
        llm_kwargs={
            "model": config.llm,
            "generation_kwargs": {"temperature": float(config.temperature)},
        },
    )

    while True:
        try:
            question = input("Question: ")
            response = pipeline.run(
                {
                    "prompt_builder": {"question": question},
                    "router": {"question": question},
                }
            )
            if "cleaner" in response.keys():
                print(response["cleaner"]["documents"][0].json)
            elif "router" in response.keys():
                print(response["router"]["fallback_reply"])
            else:
                raise Exception(response)

        except KeyboardInterrupt:
            print("exiting...")
            sys.exit(0)
