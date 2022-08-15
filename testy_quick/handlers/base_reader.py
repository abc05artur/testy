from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd

class BaseReader(ABC):
    """
    metaclass to control readers.
    """
    __readers: Dict[str, "BaseReader"] = dict()

    def __new__(cls, *args, **kwargs):
        if "name" not in kwargs:
            raise TypeError("Constructor of a BaseReader object must have a keyword 'name' argument as registry key. "
                            f"Solution: Modify the initializer function of {cls} and/or the call.")
        name = kwargs["name"]
        if not isinstance(name,str) or not name:
            raise TypeError("Name must be a non-empty string.")
        if name in cls.__readers:
            raise KeyError(f"A reader with the name {name} already exists. "
                           f"Use a different name form {cls.available_readers()}. "
                           f"FYI: {cls.readers_df()}")
        x = super().__new__(cls)
        cls.__readers[name] = x
        return x

    @classmethod
    def get_reader(cls, name: str) -> "BaseReader":
        if name not in cls.__readers:
            raise KeyError()
        return cls.__readers[name]

    @classmethod
    def available_readers(cls) -> List[str]:
        return list(cls.__readers.keys())
    @classmethod
    def readers_df(cls):
        ans=pd.DataFrame(columns=["name","class","object","description"])
        for n,o in cls.__readers.items():
            d={"name":n,"class":str(o.__class__),"object":str(o),"description":o.__doc__}
            ans=ans.append(d,ignore_index=True)
        return ans

    @abstractmethod
    def read(self, file_name, var_name):
        print("called BaseReader.read")