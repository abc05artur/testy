from typing import Dict, List

import pandas as pd


class _Registered:
    __registered: Dict[str, "_Registered"] = dict()

    def __new__(cls, *args, **kwargs):
        if "name" not in kwargs:
            raise TypeError("Constructor of a registered object must have a keyword 'name' argument as registry key. "
                            f"Solution: Modify the initializer function of {cls} and/or the call.")
        name = kwargs["name"]
        if not isinstance(name, str) or not name:
            raise TypeError("Name must be a non-empty string.")
        if name in cls.__registered:
            raise KeyError(f"A reader with the name {name} already exists. "
                           f"Use a different name form {cls.available_handlers()}. "
                           f"FYI: {cls.handlers_df()}")
        x = super().__new__(cls)
        cls.__registered[name] = x
        return x

    @classmethod
    def get_handler(cls, name: str) -> "_Registered":
        if name not in cls.__registered:
            raise KeyError(
                f"No handler named {name}. Available handlers: {cls.available_handlers()}. Call {cls}.handlers_df() for full info.")
        ans = cls.__registered[name]
        if not isinstance(ans, cls):
            raise TypeError(f"Handler {name} is of type {ans.__class__}, not {cls}")
        return ans

    @classmethod
    def available_handlers(cls) -> List[str]:
        return list(cls.__registered.keys())

    @classmethod
    def handlers_df(cls):
        ans = pd.DataFrame(columns=["name", "class", "object", "description"])
        for n, o in cls.__registered.items():
            d = {"name": n, "class": str(o.__class__), "object": str(o), "description": o.__doc__}
            ans = ans.append(d, ignore_index=True)
        return ans
