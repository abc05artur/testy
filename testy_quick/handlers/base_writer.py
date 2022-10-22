import json
from abc import ABC, abstractmethod
from typing import Dict, Any

from testy_quick.handlers._registered import _Registered


class BaseWriter(_Registered, ABC):
    """
    metaclass to control writers.
    """
    @abstractmethod
    def write(self,complete_file_name:str, var_dict:Dict[str,Any])->None:
        pass

class JsonWriter(BaseWriter):
    def write(self, complete_file_name: str, var_dict: Dict[str, Any]) -> None:
        s=json.dumps(var_dict,indent=4)
        with open(complete_file_name,"w") as f:
            f.write(s)

class JsonSingleWriter(BaseWriter):
    def write(self, complete_file_name: str, var_dict: Dict[str, Any]) -> None:
        l=list(var_dict.values())
        if len(l)!=1:
            raise ValueError(f"only one value can be written with {self.__class__}")
        s=json.dumps(l[0],indent=4)
        with open(complete_file_name,"w") as f:
            f.write(s)