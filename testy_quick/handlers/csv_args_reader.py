import pandas as pd

from testy_quick.handlers import BaseReader


class CsvArgsReader(BaseReader):
    def __init__(self, name, **read_kwargs):
        self.read_kwargs = read_kwargs

    def read(self, complete_file_name, var_name):
        df = pd.read_csv(complete_file_name, **self.read_kwargs)
        return df