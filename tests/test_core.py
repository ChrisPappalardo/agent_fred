from eparse.interfaces import ExcelParse

from agent_fred.core import load_prompt, xlsx_to_haystack_docs, xlsx_to_db


def test_load_prompt() -> None:
    """test load rag prompt"""
    prompt = load_prompt("src/agent_fred/prompts/rag.txt")
    assert "helpful" in prompt


def test_xlsx_to_haystack_docs() -> None:
    """test xls converts to haystack docs"""
    docs = xlsx_to_haystack_docs("tests/test_data/GDPC1_1.xls")
    assert len(docs) > 0


def test_xlsx_to_db() -> None:
    """test xls loads into database"""
    xlsx_to_db("tests/test_data/GDPC1_1.xls")
    assert len(ExcelParse.select()) > 0
