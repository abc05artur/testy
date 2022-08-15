from .base_reader import BaseReader

import pandas as pd


class CsvReader(BaseReader):
    def read(self, file_name, var_name):
        df=pd.read_csv(file_name)
        return df
