from abc import ABC


class Plugin(ABC):
    name = "base"

    def query(self, question):
        raise NotImplementedError
