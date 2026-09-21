class EnergyManager:

    def __init__(self, energy=100):
        self.energy = energy

    def consume(self, amount):
        self.energy -= amount

    def available(self):
        return self.energy

    def can_afford(self, amount):
        return self.energy >= amount

    def mode(self):
        if self.energy <= 5:
            return "SURVIVAL"

        if self.energy <= 20:
            return "OPTIMIZATION"

        return "EXPLORATION"
