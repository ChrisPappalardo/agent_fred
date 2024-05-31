import re
from pytest_mock.plugin import MockerFixture

from haystack.components.fetchers import LinkContentFetcher
from haystack.dataclasses import ByteStream, Document
from haystack.utils import Secret

from agent_fred.components import (
    CustomConditionalRouter,
    JsonDocument,
    FredCleaner,
    FredFetcher,
)


def test_custom_conditional_router() -> None:
    """test custom conditional router"""

    def my_func(value: str):
        patt = r'my_func\("(.*?)",\s?"(.*?)",\s?"(.*?)"\)'
        match = re.search(patt, value, re.DOTALL)
        return match.groups() if match else None

    routes = [
        {
            "condition": "{{ value|custom_filter != None }}",
            "output": "{{ value|custom_filter }}",
            "output_name": "good_route",
            "output_type": str,
        },
        {
            "condition": "{{ value|custom_filter == None }}",
            "output": "bad route: {{ value }}",
            "output_name": "bad_route",
            "output_type": str,
        },
    ]
    router = CustomConditionalRouter(custom_filter=my_func, routes=routes)
    result = router.run(value='my_func("1", "2", "3")')
    assert "good_route" in result.keys()
    assert result["good_route"] == ("1", "2", "3")
    result = router.run(value="my_func(1, 2, 3)")
    assert "bad_route" in result.keys()
    assert result["bad_route"] == "bad route: my_func(1, 2, 3)"


def test_json_document() -> None:
    """test json document"""
    document = JsonDocument(content='{"test": 123}')
    assert isinstance(document, Document)
    assert hasattr(document, "json")
    assert isinstance(document.json, dict)
    assert document.json["test"] == 123


def test_fred_api_fetcher(mocker: MockerFixture) -> None:
    """test the fred api fetcher"""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.content_type = "application/json"
    mock_get.return_value.json.return_value = {"test": "data"}
    component = FredFetcher(api_key=Secret.from_token("testkey"))
    assert isinstance(component, LinkContentFetcher)
    assert hasattr(component, "raise_on_failure")
    inputs = {
        "series_id": "GPDC1",
        "start_date": "2021-01-01",
        "end_date": "2021-01-01",
    }
    result = component.run(inputs)
    assert isinstance(result, dict)
    assert isinstance(result["streams"], list)
    assert isinstance(result["streams"][0], ByteStream)
    assert result["streams"][0].meta["fred_url_kwargs"] == inputs


def test_fred_api_cleaner(mocker: MockerFixture) -> None:
    """test the fred api cleaner"""
    cleaner = FredCleaner()
    bs = ByteStream.from_string(
        '{"observations": [{"date": "2021-01-01", "value": "123"}]}'
    )
    bs.meta = {"fred_url_kwargs": {"test": 123}}
    result = cleaner.run(streams=[bs])
    assert isinstance(result, dict)
    assert isinstance(result["documents"], list)
    assert isinstance(result["documents"][0], JsonDocument)
    assert "observations" not in result["documents"][0].content
    assert result["documents"][0].meta["fred_url_kwargs"] == {"test": 123}
