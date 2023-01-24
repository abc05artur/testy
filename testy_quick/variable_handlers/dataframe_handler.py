from pathlib import Path
from typing import Any

import pandas as pd

from .base_handler import DefaultSingleHandler


class DataframeHandler(DefaultSingleHandler):

    def condition(self, variable_value: Any) -> bool:
        if isinstance(variable_value, pd.DataFrame):
            if variable_value.index.nlevels == 1:
                for i, v in enumerate(variable_value.index):
                    if i != v:
                        return False
                if variable_value.columns.nlevels == 1:
                    return True
        return False

    def _write(self, var_name: str, var_value: pd.DataFrame, folder_path: Path) -> None:
        folder_path.mkdir(parents=True, exist_ok=True)
        var_value.to_csv(folder_path / (var_name + ".csv"), index=False)

    def _read(self, var_name: str, folder_path: Path) -> pd.DataFrame:
        return pd.read_csv(folder_path / (var_name + ".csv"))

    def write_report(self, expected_value: Any, actual_value: Any, folder_path: Path, var_name: str) -> None:
        pass

    def _compare(self, expected_value: pd.DataFrame, actual_value: pd.DataFrame) -> bool:
        return expected_value.equals(actual_value)
