from .base_reader import BaseReader
from .base_comparer import BaseComparer
from .csv_reader import CsvReader
from .base_answer import BaseAnswer
from .dataframe_default_comparer import DataframeDefaultComparer
from .csv_default_answer import CsvDefaultAnswer
from .default_comparer import DefaultComparer
from .json_reader import JsonReader
from .default_json_answer import DefaultJsonAnswer
from .indexed_dataframe_answer import CsvArgsReader
from .indexed_dataframe_answer import DataframeIndexedComparer
from .indexed_dataframe_answer import IndexedDataframeAnswer


default_csv_answer = CsvDefaultAnswer(name="csv")
default_csv_reader = default_csv_answer
default_json_answer= DefaultJsonAnswer(name="json")
default_json_reader= default_json_answer
default_comparer = default_json_answer
