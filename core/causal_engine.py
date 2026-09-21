class CausalEngine:

    def create_rule(self, cause, effect, confidence):
        return {
            "cause": cause,
            "effect": effect,
            "confidence": confidence
        }
