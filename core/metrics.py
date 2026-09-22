class Metrics:

    @staticmethod
    def curiosity_index(new, total):
        return new / max(total, 1)

    @staticmethod
    def adaptation_index(improvement, time):
        return improvement / max(time, 1)

    @staticmethod
    def learning_efficiency(knowledge, energy):
        return knowledge / max(energy, 1)

    @staticmethod
    def innovation_index(unique_actions_explored: int, rejected_constraints: int) -> float:
        """
        Computes the Innovation Index (II):
        Measures the agent's semantic divergence from failures.
        Higher value indicates bold exploration orthogonal to past constraints.
        """
        if rejected_constraints == 0:
            return 1.0
        return round(min(5.0, (unique_actions_explored / max(1, rejected_constraints)) * 1.5), 2)

