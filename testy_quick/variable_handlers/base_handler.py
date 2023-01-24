from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Iterable, Union, Tuple

from testy_quick.low_level import TestyError


class BaseHandler(ABC):
    @abstractmethod
    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        pass

    @abstractmethod
    def read(self, var_names: Iterable[str], folder_path: Path) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _compare(self, expected_value: Any, actual_value: Any) -> bool:
        pass

    def compare(self, expected_value: Any, actual_value: Any) -> Tuple[bool, Union[bool, BaseException]]:
        try:
            return (True, self._compare(expected_value, actual_value))
        except Exception as e:
            return (False, e)

    def write_report(self, expected_value: Any, actual_value: Any, folder_path: Path, var_name: str) -> None:
        pass

    def get_report(self, expected_value: Any, actual_value: Any, var_name: str) -> str:
        return f"override '{self.get_report.__name__}' method for '{self.__class__.__name__}' class " \
               f"to have a report shown here."


class SingleHandler(BaseHandler, ABC):
    @abstractmethod
    def _write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        """

        """
        pass

    @abstractmethod
    def _read(self, var_name: str, folder_path: Path) -> Any:
        pass

    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        for var_name, var_value in var_dict.items():
            try:
                self._write(var_name=var_name, var_value=var_value, folder_path=folder_path)
            except FileNotFoundError as e:
                raise TestyError(
                    f"Failed to write {var_name}, most likely cause is handler did not create the folder.") from e
            except Exception as e:
                raise TestyError(f"Failed to write {var_name}") from e

    def read(self, var_names: Iterable[str], folder_path: Path) -> Dict[str, Any]:
        answer = dict()
        for var_name in var_names:
            try:
                var_value = self._read(var_name, folder_path)
            except Exception as e:
                raise TestyError(f"Failed to read {var_name}") from e
            answer[var_name] = var_value
        return answer


class MultiHandler(BaseHandler, ABC):
    @abstractmethod
    def _write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        pass

    @abstractmethod
    def _read(self, folder_path: Path) -> Dict[str, Any]:
        pass

    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        try:
            self._write(var_dict, folder_path)
        except Exception as e:
            raise TestyError(f"Multi writing failed for vars {var_dict.keys()}.") from e

    def read(self, var_names: Iterable[str], folder_path: Path) -> Dict[str, Any]:
        var_names = list(var_names)
        if len(var_names) == 0:
            return dict()
        try:
            var_dict = self._read(folder_path)
        except Exception as e:
            raise TestyError(f"Multi reading from {folder_path} failed for vars {var_names}.") from e
        ans_d = dict()
        not_found = list()
        for var_name in var_names:
            if var_name in var_dict:
                ans_d[var_name] = var_dict[var_name]
            else:
                not_found.append(var_name)
        if len(not_found) > 0:
            raise TestyError(f"Multi reading from {folder_path} din not find vars {not_found}.")
        return ans_d


class DefaultHandler(ABC):
    @abstractmethod
    def condition(self, variable_value: Any) -> bool:
        pass


class DefaultSingleHandler(SingleHandler, DefaultHandler, ABC):
    pass


class DefaultMultiHandler(MultiHandler, DefaultHandler, ABC):
    pass
