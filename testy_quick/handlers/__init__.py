from .base_reader import BaseReader
from .base_comparer import BaseComparer
from .csv_reader import CsvReader
from .base_answer import BaseAnswer
from .dataframe_default_comparer import DataframeDefaultComparer
from .csv_default_answer import CsvDefaultAnswer
from .default_comparer import DefaultComparer


default_csv_answer = CsvDefaultAnswer(name="csv")
default_csv_reader = default_csv_answer
