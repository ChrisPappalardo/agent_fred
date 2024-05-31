import json
import pandas as pd
import requests
from typing import Any, Optional

from haystack import Document

from agent_fred.config import config


def clean_fred_api_json(data: dict[str, Any]) -> str:
    """clean and return fred api json data"""
    result = []
    for d in json.loads(data)["observations"]:
        result.append({"date": d["date"], "value": d["value"]})
    return json.dumps(result)


def fred_api_to_documents(
    data: list[dict[str, str]],
    meta: Optional[dict] = {},
) -> list[Document]:
    """return a list of documents for each fred api element"""
    series_id = meta["fred_url_kwargs"]["series_id"]
    return [
        Document(
            content=f'Value for {series_id} on {rec["date"]} was {rec["value"]}.',
            meta=meta,
        )
        for rec in data
    ]


def get_fred_data_url(
    series_id: str,
    start_date: str,
    end_date: str,
    file_type: str = "json",
) -> str:
    """construct fred api url"""
    return (
        f"https://api.stlouisfed.org/fred/series/observations?"
        f"series_id={series_id}&"
        f"realtime_start={end_date}&"
        f"realtime_end={end_date}&"
        f"observation_start={start_date}&"
        f"observation_end={end_date}&"
        f"file_type={file_type}&"
        f"api_key={config.fred_api_key}"
    )


def get_fred_data_series(
    series_id: str,
    start_date: str,
    end_date: str,
    file_type: str = "json",
    clean: bool = True,
) -> pd.DataFrame:
    """get and return fred data series as json"""
    url = get_fred_data_url(series_id, start_date, end_date, file_type)
    result = json.dumps(requests.get(url).json())
    if clean:
        return clean_fred_api_json(result)
    return json.dumps(result)


def load_prompt(filename: str) -> str:
    """load and return prompt template"""
    with open(filename) as f:
        return f.read()
