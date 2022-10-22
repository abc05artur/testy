from abc import ABC

from . import BaseReader, BaseComparer


class BaseAnswer(BaseReader, BaseComparer, ABC):
    pass
