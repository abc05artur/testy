import os

BASE_DATA_FOLDER = os.path.join("testy", "data")

INPUT_META_FILE_NAME = "input_meta.csv"
INPUT_META_READER = ("csv", "")
INPUT_META_VAR_COL = "var_name"
INPUT_META_FILE_COL = "file_name"
INPUT_META_READER_COL = "reader_name"
INPUT_META_NAMED_COL = "is_named"

OUTPUT_META_FILE_NAME = "output_meta.csv"
OUTPUT_META_READER = ("csv", "")
OUTPUT_META_VAR_COL = "var_name"
OUTPUT_META_FILE_COL = "file_name"
OUTPUT_META_READER_COL = "handler_name"
