from typing import Dict, List, Tuple, Union, Callable, Any

from .base_handler import BaseHandler
from .conditions import is_json
from .json_handler import JsonSingleHandler
from ..others import TestyError

json_single_name = "default_json_single"

registered_handlers: Dict[str, BaseHandler] = {
    json_single_name: JsonSingleHandler()
}


def register_handler(handler_unique_name: str, handler_instance: BaseHandler) -> None:
    # todo: docstring
    if handler_unique_name in registered_handlers:
        raise TestyError(f"handler named {handler_unique_name} already registered")
    registered_handlers[handler_unique_name] = handler_instance


default_order: List[Tuple[Union[type, Callable[[Any], bool]], str]] = [
    (is_json, json_single_name),
]
