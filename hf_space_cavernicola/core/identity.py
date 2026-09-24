import json


class Identity:

    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def purpose(self):
        return self.data["purpose"]

    def principles(self):
        return self.data["principles"]
