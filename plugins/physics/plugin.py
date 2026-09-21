from plugins.base import Plugin


class PhysicsPlugin(Plugin):
    name = "physics"

    def query(self, question):
        if question == "gravity":
            return {
                "value": 9.81
            }
        return None
