from abc import ABC, abstractmethod

from testy_quick.handlers._registered import _Registered


class BaseReader(_Registered, ABC):
    """
    metaclass to control readers.
    """

    @abstractmethod
    def read(self, complete_file_name, var_name):
        print("called BaseReader.read")

