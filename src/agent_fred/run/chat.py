import sys

from haystack.dataclasses import ChatMessage

from agent_fred.config import config
from agent_fred.core import load_prompt, fred_api_to_documents
from agent_fred.pipelines import fred_chat_pipeline


if __name__ == "__main__":
    print("agent chat pipeline for q&a on fred api using nlp")
    print(f"using {config.embedding_model} embeddings and {config.llm} llm")

    # create pipeline, document store, and document embedder
    pipeline, document_store = fred_chat_pipeline(
        agent_prompt_template=load_prompt("src/agent_fred/prompts/agent.txt"),
        chat_prompt_template=load_prompt("src/agent_fred/prompts/chat.txt"),
        api_key=config.fred_api_key,
        agent_llm_kwargs={
            "model": config.llm,
            "generation_kwargs": {"temperature": float(config.temperature)},
        },
        chat_llm_kwargs={
            "model": config.llm,
            "generation_kwargs": {"temperature": float(config.temperature)},
        },
    )

    history = []

    while True:
        try:
            assistant = ""
            question = input("Question: ")
            response = pipeline.run(
                {
                    "chat_prompt_builder": {
                        "template_variables": {
                            "question": question,
                            "history": history,
                        },
                    },
                    "prompt_builder": {"question": question},
                    "router": {"question": question},
                },
            )

            history.append(f"User: {question}")

            if "cleaner" in response.keys():
                doc = response["cleaner"]["documents"][0]
                documents = fred_api_to_documents(doc.json, doc.meta)
                document_store.write_documents(documents)
                print(doc.json)
            else:
                assistant = response["chat_llm"]["replies"][0].content
                history.append(f"Assistant: {assistant}")
                print(assistant)

        except KeyboardInterrupt:
            print("exiting...")
            sys.exit(0)
