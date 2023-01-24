from typing import Dict, Set, List, Tuple, Callable, Any

from .base_handler import BaseHandler, DefaultHandler
from .conditions import condition_for_dataframe_handler
from .exception_handler import ExceptionHandler
from .json_handler import JsonMultiHandler, JsonSingleHandler

from ..low_level import TestyError
from ..strings import default_dataframe, default_testy_json_multi, default_testy_json_single, default_exception_handler

__existing_handler_names: Set[str] = set()
__extended_handler_conditions: Dict[str, str] = dict()
__default_handler_order: List[Tuple[str, DefaultHandler]] = list()


def __dev_register(handler: DefaultHandler, name: str) -> None:
    if name in __existing_handler_names:
        raise TestyError(f"Internal initialization error: handler named '{name}' already registered.")
    if name in __extended_handler_conditions:
        raise TestyError(f"Internal initialization error: handler named '{name}' already exists in extended.")
    __existing_handler_names.add(name)
    __default_handler_order.append((name, handler))


def __dev_declare(name: str, str_cond: str):
    if name in __existing_handler_names:
        raise TestyError(f"Internal initialization error: handler named '{name}' already registered.")
    if name in __extended_handler_conditions:
        raise TestyError(f"Internal initialization error: handler named '{name}' already exists in extended.")
    __extended_handler_conditions[name] = str_cond


if condition_for_dataframe_handler:
    from .dataframe_handler import DataframeHandler

    __dev_register(DataframeHandler(), default_dataframe)
else:
    __dev_declare(default_dataframe, "pandas")

__dev_register(ExceptionHandler(), default_exception_handler)

__dev_register(JsonMultiHandler(), default_testy_json_multi)

__dev_register(JsonSingleHandler(), default_testy_json_single)

default_order: List[Tuple[Callable[[Any], bool], str]] = \
    [(handler.condition, name) for name, handler in __default_handler_order]
registered_handlers: Dict[str, BaseHandler] = {name: handler for name, handler in __default_handler_order}
extended_handlers_conditions: Dict[str, str] = __extended_handler_conditions
