from . import BaseAnswer, CsvArgsReader, DataframeIndexedComparer


class IndexedDataframeAnswer(BaseAnswer, CsvArgsReader, DataframeIndexedComparer):
    def __init__(self, index_cols, name, **read_kwargs):
        CsvArgsReader.__init__(self, name=name, **read_kwargs)
        DataframeIndexedComparer.__init__(self, index_cols, name=name)
