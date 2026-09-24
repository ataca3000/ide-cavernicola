class PurposeFilter:

    def __init__(self, active_goal=None):
        self.active_goal = active_goal or "Default Objective"

    def evaluate(self, goal_score):
        return goal_score >= 0.5
