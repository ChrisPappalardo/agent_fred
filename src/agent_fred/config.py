import logging
import os


class Config:
    debug = None
    prompt_filename = None
    embedding_model = None
    llm = None
    temperature = None


config = Config()


# load env vars
config.debug = os.environ.get(
    "RAG_DEBUG",
    False,
)
config.prompt_filename = os.environ.get(
    "RAG_PROMPT",
    "src/agent_fred/prompts/rag.txt",
)
config.embedding_model = os.environ.get(
    "RAG_EMBEDDINGS",
    "phi3",
)
config.llm = os.environ.get(
    "RAG_LLM",
    "phi3",
)
config.temperature = os.environ.get(
    "RAG_TEMPERATURE",
    0.0,
)


# enable haystack logging
if config.debug:
    logging.basicConfig(
        format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
    )
    logging.getLogger("haystack").setLevel(logging.INFO)
