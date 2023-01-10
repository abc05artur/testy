import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Union, List, Tuple, Callable, Iterable

from testy_quick.low_level import TestyError, is_json, is_json_short
from testy_quick.strings import default_testy_json_single, default_exception_handler, default_testy_json_multi


class BaseHandler(ABC):
    @abstractmethod
    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        pass

    @abstractmethod
    def read(self, var_names: Iterable[str], folder_path: Path) -> Dict[str, Any]:
        pass

    @abstractmethod
    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        pass

    @abstractmethod
    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path, var_name: str) -> None:
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

    def read(self, var_names: Iterable[str], folder_path: Path) -> Dict[str, Any]:
        answer = dict()
        for var_name in var_names:
            try:
                var_value = self.user_def_read(var_name, folder_path)
            except Exception as e:
                raise TestyError(f"Failed to read {var_name}") from e
            answer[var_name] = var_value
        return answer


class MultiHandler(BaseHandler):
    @abstractmethod
    def user_def_write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        pass

    @abstractmethod
    def user_def_read(self, folder_path: Path) -> Dict[str, Any]:
        pass

    def write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        try:
            self.user_def_write(var_dict, folder_path)
        except Exception as e:
            raise TestyError(f"Multi writing failed for vars {var_dict.keys()}.") from e

    def read(self, var_names: Iterable[str], folder_path: Path) -> Dict[str, Any]:
        var_names = list(var_names)
        if len(var_names) == 0:
            return dict()
        try:
            var_dict = self.user_def_read(folder_path)
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


class JsonSingleHandler(SingleHandler):

    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path, var_name) -> None:
        raise NotImplementedError()

    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        raise NotImplementedError()

    def user_def_read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".json"), "r") as f:
            var_value = json.load(f)
        return var_value

    def user_def_write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        with open(folder_path / (var_name + ".json"), "w") as f:
            json.dump(var_value, f, indent=2)


class JsonMultiHandler(MultiHandler):
    file_name = "default_json_muti.json"

    def user_def_read(self, folder_path: Path) -> Dict[str, Any]:
        with open(folder_path / self.file_name, "r") as f:
            ans_d = json.load(f)
        return ans_d

    def user_def_write(self, var_dict: Dict[str, Any], folder_path: Path) -> None:
        with open(folder_path / self.file_name, "w") as f:
            json.dump(var_dict, f, indent=2)

    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path, var_name) -> None:
        raise NotImplementedError()

    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        raise NotImplementedError()


class ExceptionHandler(SingleHandler):

    def exception_to_dict(self, e: BaseException):
        ans = dict()
        ans["type"] = str(type(e))
        ans["args"] = e.args
        if e.__cause__ is not None:
            ans["inner"] = self.exception_to_dict(e.__cause__)
        return ans

    def write_report(self, expected_answer: Any, actual_answer: Any, folder_path: Path, var_name) -> None:
        if isinstance(expected_answer, Exception):
            expected_answer = self.exception_to_dict(expected_answer)
        expected_answer = json.dumps(expected_answer, indent=2)
        if isinstance(actual_answer, Exception):
            actual_answer = self.exception_to_dict(actual_answer)
        actual_answer = json.dumps(actual_answer, indent=2)
        with open(folder_path / (var_name + ".json"), "r") as f:
            f.write(expected_answer)
            f.write(actual_answer)

    def is_same(self, expected_answer: Any, actual_answer: Any) -> bool:
        if isinstance(expected_answer, Exception):
            expected_answer = self.exception_to_dict(expected_answer)
        expected_answer = json.dumps(expected_answer, indent=2)
        if isinstance(actual_answer, Exception):
            actual_answer = self.exception_to_dict(actual_answer)
        actual_answer = json.dumps(actual_answer, indent=2)
        return actual_answer == expected_answer

    def user_def_read(self, var_name: str, folder_path: Path) -> Any:
        with open(folder_path / (var_name + ".json"), "r") as f:
            var_value = json.load(f)
        return var_value

    def user_def_write(self, var_name: str, var_value: Any, folder_path: Path) -> None:
        if isinstance(var_value, Exception):
            var_value = self.exception_to_dict(var_value)
        with open(folder_path / (var_name + ".json"), "w") as f:
            json.dump(var_value, f, indent=2)


handlers: Dict[str, BaseHandler] = {
    default_testy_json_single: JsonSingleHandler(),
    default_testy_json_multi: JsonMultiHandler(),
    default_exception_handler: ExceptionHandler(),
}
default_order: List[Tuple[Union[type, Callable[[Any], bool]], str]] = [
    (is_json_short, default_testy_json_multi),
    (is_json, default_testy_json_single),
]
