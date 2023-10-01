import abc
import dataclasses
import time
from typing import List, Dict, Any, Callable


@dataclasses.dataclass(kw_only=True)
class SqliteDataObject(abc.ABC):
    created_at: float = None
    updated_at: float = None

    @classmethod
    @abc.abstractmethod
    def primary_keys(cls) -> List[str]:
        ...

    @classmethod
    def extra_indexes(cls) -> List[List[str]]:
        return []

    @classmethod
    def unique_keys(cls) -> List[List[str]]:
        return []

    @classmethod
    def loads(cls, json_obj: Dict[str, Any]) -> "SqliteDataObject":
        function_mapping = cls._customized_mapping_function("_load__")
        return cls(
            **{
                field.name: function_mapping[field.name](json_obj.get(field.name))
                for field in dataclasses.fields(cls)
            }
        )

    def dumps(self) -> Dict[str, Any]:
        function_mapping = self._customized_mapping_function("_dump__")
        return {
            field.name: function_mapping[field.name](getattr(self, field.name))
            for field in dataclasses.fields(self)
        }

    @classmethod
    def field_map(cls) -> Dict[str, dataclasses.Field]:
        return {field.name: field for field in dataclasses.fields(cls)}

    @classmethod
    def fields(cls) -> List[dataclasses.Field]:
        return list(dataclasses.fields(cls))

    @classmethod
    def field_names(cls) -> List[str]:
        return [field.name for field in dataclasses.fields(cls)]

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__

    @classmethod
    def _dump__created_at(cls, value: float) -> float:
        return value or time.time()

    @classmethod
    def _dump__updated_at(cls, value: float) -> float:
        return time.time()

    @classmethod
    def _customized_mapping_function(
        cls, prefix: str
    ) -> Dict[str, Callable[[Any], Any]]:
        all_functions = {
            item: getattr(cls, item)
            for item in dir(cls)
            if isinstance(getattr(cls, item), Callable)
        }
        return {
            field: all_functions.get(prefix + field, lambda x: x)
            for field in cls.field_names()
        }
