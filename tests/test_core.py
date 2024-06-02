import os

from eparse.interfaces import ExcelParse

from agent_fred.core import (
    load_prompt,
    xlsx_to_serialized_list,
    xlsx_to_haystack_docs,
    xlsx_to_db,
)


def test_config() -> None:
    """test config works"""
    os.environ["RAG_DEBUG"] = "True"
    from agent_fred.config import config

    assert hasattr(config, "debug")
    assert config.debug is not False or None


def test_load_prompt() -> None:
    """test load rag prompt"""
    prompt = load_prompt("src/agent_fred/prompts/rag.txt")
    assert "helpful" in prompt


def test_xlsx_to_serialized_list() -> None:
    """test xls converts to serialized list"""
    serialized_list = xlsx_to_serialized_list("tests/test_data/GDPC1_1.xls")
    assert len(serialized_list) > 0


def test_xlsx_to_haystack_docs() -> None:
    """test xls converts to haystack docs"""
    docs = xlsx_to_haystack_docs("tests/test_data/GDPC1_1.xls")
    assert len(docs) > 0


def test_xlsx_to_db() -> None:
    """test xls loads into database"""
    xlsx_to_db("tests/test_data/GDPC1_1.xls")
    assert len(ExcelParse.select()) > 0
