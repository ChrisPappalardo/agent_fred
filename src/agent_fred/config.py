import logging
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    debug = None
    prompt_filename = None
    embedding_model = None
    llm = None
    temperature = None
    fred_api_key = None


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
config.fred_api_key = os.environ.get(
    "FRED_API_KEY",
    None,
)


# enable haystack logging
if config.debug:
    logging.basicConfig(
        format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
    )
    logging.getLogger("haystack").setLevel(logging.INFO)
