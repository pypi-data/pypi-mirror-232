import abc
import json
from typing import TypeAlias

DictList: TypeAlias = list[dict[str, str]]


class BaseRenderer(abc.ABC):
    @abc.abstractmethod
    def render(self, data: DictList) -> str:
        pass


class JSONRenderer(BaseRenderer):
    def render(self, data: DictList) -> str:
        return json.dumps(data, ensure_ascii=False, indent=4)
