import json

from .base_reader import BaseReader


class JsonReader(BaseReader):
    def read(self, complete_file_name, var_name):
        d = json.load(open(complete_file_name, "r"))
        return d[var_name]
