import json
from pytest_mock.plugin import MockerFixture

from agent_fred.config import config
from agent_fred.core import (
    fred_api_to_documents,
    get_fred_data_series,
    load_prompt,
)


def test_config() -> None:
    """test config works"""
    assert hasattr(config, "debug")


def test_fred_api_to_documents() -> None:
    data = [
        {"date": "2021-01-01", "value": "123"},
        {"date": "2021-12-31", "value": "456"},
    ]
    meta = {"fred_url_kwargs": {"series_id": "test_series"}}
    documents = fred_api_to_documents(data, meta)
    assert len(documents) == 2
    assert documents[0].content == "Value for test_series on 2021-01-01 was 123."


def test_get_fred_data_series(mocker: MockerFixture) -> None:
    """test get fred data series function"""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.content_type = "application/json"
    mock_get.return_value.json.return_value = {
        "observations": [{"date": "2021-12-31", "value": "123"}]
    }
    ds = get_fred_data_series("GDPC1", "2021-01-01", "2021-12-31")
    assert isinstance(ds, str)
    assert len(json.loads(ds)) == 1
    assert json.loads(ds)[0]["date"] == "2021-12-31"
    assert json.loads(ds)[0]["value"] == "123"


def test_load_prompt() -> None:
    """test load rag prompt"""
    prompt = load_prompt("src/agent_fred/prompts/chat.txt")
    assert "Relevant Federal" in prompt
