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
