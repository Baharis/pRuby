

class RoutineManager:
    """
    A class to menage all routines. Its utility includes building routines,
    remembering which routines are defined and so on.
    """
    def __init__(self):
        self.defined = list()

    def default(self):
        return self.defined[0]

    def subscribe(self, new_method):
        if not(new_method in self.defined):
            self.defined.append(new_method)
