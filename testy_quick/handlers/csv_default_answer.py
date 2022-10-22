from . import CsvReader, DataframeDefaultComparer, BaseAnswer


class CsvDefaultAnswer(CsvReader, DataframeDefaultComparer,BaseAnswer):
    pass
