from pathlib import Path
import os
from typing import Union


def delete_f(foler_path: Union[Path, str]):
    if isinstance(foler_path, str):
        foler_path = Path(foler_path)
    if foler_path.is_file():
        os.remove(foler_path)
    elif foler_path.is_dir():
        for f in foler_path.iterdir():
            delete_f(f)
        foler_path.rmdir()
    # else:
    #     raise Exception("No such path I guess")


temp_data_path = Path("temp_data")

if __name__ == "__main__":
    p = Path("..") / "fff/t4/case_0"
    delete_f(p)
