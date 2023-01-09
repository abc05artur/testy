from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from testy_quick.others import TestyError


class BaseHandler(ABC):
    @abstractmethod
    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        pass

    @abstractmethod
    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        pass

    @abstractmethod
    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path) -> None:
        pass

class SingleHandler(BaseHandler):
    @abstractmethod
    def user_def_write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        pass

    @abstractmethod
    def user_def_read(self, var_name: str, folder_path: Path) -> Any:
        pass

    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        for var_name, var_value in var_dict.items():
            try:
                self.user_def_write(var_name=var_name, var_value=var_value, folder_path=folder_path)
            except Exception as e:
                raise TestyError(f"Failed to write {var_name}") from e
