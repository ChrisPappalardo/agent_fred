import json
from dataclasses import dataclass
from jinja2.nativetypes import NativeEnvironment
from typing import Any, Callable, List, Set

from haystack import component
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.routers import ConditionalRouter
from haystack.components.routers.conditional_router import (
    NoRouteSelectedException,
    RouteConditionException,
)
from haystack.dataclasses import ByteStream, Document
from haystack.utils import Secret

from agent_fred.core import clean_fred_api_json, get_fred_data_url


# generic
# -----------------------------------------------------------------------------
@component
class CustomConditionalRouter(ConditionalRouter):
    """conditional router that accepts a callable and adds it as a filter"""

    custom_filter = None

    def __init__(self, custom_filter: Callable, **kwargs):
        """add custom_filter to object"""
        self.custom_filter = custom_filter
        super(CustomConditionalRouter, self).__init__(**kwargs)

    def run(self, **kwargs):
        """add custom_filter to the conditional router run"""
        env = NativeEnvironment()
        env.filters["custom_filter"] = self.custom_filter

        # this is the same as ConditionalRouter
        for route in self.routes:
            try:
                t = env.from_string(route["condition"])
                if t.render(**kwargs):
                    t_output = env.from_string(route["output"])
                    output = t_output.render(**kwargs)
                    return {route["output_name"]: output}
            except Exception as e:
                raise RouteConditionException(
                    f"Error evaluating condition for route '{route}': {e}"
                ) from e

        raise NoRouteSelectedException(f"No route fired. Routes: {self.routes}")

    def _extract_variables(
        self,
        env: NativeEnvironment,
        templates: List[str],
    ) -> Set[str]:
        """add custom_filter to env"""
        env = NativeEnvironment()
        env.filters["custom_filter"] = self.custom_filter
        return super(CustomConditionalRouter, self)._extract_variables(env, templates)


@dataclass
class JsonDocument(Document):
    """add json property and from_obj method to Document"""

    @property
    def json(self):
        return json.loads(self.content)


# fred
# -----------------------------------------------------------------------------
@component
class FredCleaner:
    """cleans fred api response"""

    @component.output_types(documents=List[JsonDocument])
    def run(self, streams: List[ByteStream]):
        result = []
        for bs in streams:
            clean = clean_fred_api_json(bs.to_string())
            result.append(JsonDocument(content=clean, meta=bs.meta))
        return {"documents": result}


@component
class FredFetcher(LinkContentFetcher):
    """fetches content from the fred api for series and dates"""

    def __init__(self, api_key: Secret, **kwargs: Any):
        self.api_key = api_key
        super(FredFetcher, self).__init__(**kwargs)

    @component.output_types(streams=List[ByteStream])
    def run(self, kwargs: dict):
        url = get_fred_data_url(**kwargs)
        result = super(FredFetcher, self).run(urls=[url])
        for bs in result["streams"]:
            bs.meta["fred_url_kwargs"] = kwargs
        return result
