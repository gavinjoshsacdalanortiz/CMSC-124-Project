class BreakException(Exception):
    """Exception to handle GTFO (break) statement"""
    pass

class ReturnException(Exception):
    """Exception to handle FOUND YR (return) statement"""
    def __init__(self, value):
        self.value = value