from typing import Tuple, Any

from .base_handler import BaseHandler
from .register import registered_handlers, default_order, extended_handlers_conditions
from ..low_level import TestyError
from ..strings import reason_var_fct


def get_handler(handler_name: str) -> BaseHandler:
    if handler_name in registered_handlers:
        return registered_handlers[handler_name]
    raise TestyError(
        f"Handler named {handler_name} is not registered. Registered handlers are {registered_handlers.keys()}")


def register_handler(handler_name: str, handler_instance: BaseHandler) -> None:
    if not isinstance(handler_name, str):
        raise TestyError(f"handler name should be str, not {type(handler_name)}")
    if len(handler_name) == 0:
        raise TestyError(f"handler name cannot be empty.")
    if not isinstance(handler_instance, BaseHandler):
        raise TestyError("handler not correct type")
    if handler_name in registered_handlers:
        raise TestyError(
            f"Handler named {handler_name} already registered. Registered handlers are {registered_handlers.keys()}")
    registered_handlers[handler_name] = handler_instance


def is_handler(handler_name: str) -> bool:
    return handler_name in registered_handlers


def is_extended_handler(handler_name: str) -> bool:
    return handler_name in extended_handlers_conditions


def condition_for_extended_handler(handler_name: str) -> str:
    return extended_handlers_conditions[handler_name]


def get_default_handler_for_var(
        var_name: str,
        var_value: Any,
) -> str:
    for condition, handler_name in default_order:
        try:
            if condition(var_value):
                return handler_name
        except Exception as e:
            raise TestyError(f"Failed to test condition for '{var_name}'. Internal error.") from e
    raise TestyError(f"Failed to find handler for '{var_name}' of type {type(var_value)}.")
