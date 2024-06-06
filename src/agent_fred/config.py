import logging
import os


class Config:
    debug = None
    prompt_filename = None
    embedding_model = None
    llm = None
    temperature = None
    api_key = None


config = Config()


# load env vars
config.debug = os.environ.get(
    "FRED_DEBUG",
    False,
)
config.embedding_model = os.environ.get(
    "FRED_EMBEDDINGS",
    "phi3",
)
config.llm = os.environ.get(
    "FRED_LLM",
    "phi3",
)
config.temperature = os.environ.get(
    "FRED_TEMPERATURE",
    0.0,
)
config.api_key = os.environ.get("API_KEY", "7a35abdb93b80fa999dea95167535ac3")


# enable haystack logging
if config.debug:
    logging.basicConfig(
        format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
    )
    logging.getLogger("haystack").setLevel(logging.INFO)
