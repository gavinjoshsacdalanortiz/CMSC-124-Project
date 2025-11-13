# custom exceptions for LOLCODE control flow statements

class BreakException(Exception):
    # Exception to handle GTFO (break) statement in loops
    pass

class ReturnException(Exception):
    # Exception to handle OMG (return) statement in functions
    def __init__(self, value):
        self.value = value