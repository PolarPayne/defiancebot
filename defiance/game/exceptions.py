class RuleException(Exception):
    pass


class StateException(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return "State was {}, but it should have been {}.".format(self.actual, self.expected)
