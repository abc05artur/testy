from testy_quick.handlers import BaseAnswer, JsonReader, DefaultComparer


class DefaultJsonAnswer(JsonReader,DefaultComparer,BaseAnswer):
    pass