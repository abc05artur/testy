from .base_reader import BaseReader

import pandas as pd


class CsvReader(BaseReader):
    def read(self, complete_file_name, var_name):
        df = pd.read_csv(complete_file_name)
        return df
