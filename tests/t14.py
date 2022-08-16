import json
import os.path
import unittest
import testy_quick.settings
from testy_quick.functions import _extract_inputs
from testy_quick.handlers import DefaultJsonAnswer
testy_quick.settings.BASE_DATA_FOLDER=os.path.join("f1")
v=_extract_inputs("t1")
print(v)
