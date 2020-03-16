class RoutineManager:
    """
    A class to menage all routines. Its utility includes building routines,
    remembering which routines are defined and so on.
    """
    def __init__(self):
        self.defined = list()

    def __getitem__(self, key):
        if not(type(key) is str):
            raise TypeError('Routine manager key should be a string')
        for routine in self.defined:
            if routine.name == key:
                return routine
        raise KeyError('No routine with name "{}" has been found'.format(key))

    @property
    def default(self):
        return self.defined[0]

    @property
    def names(self):
        return [routine.name for routine in self.defined]

    def subscribe(self, new_routine):
        if not(new_routine in self.defined):
            self.defined.append(new_routine)

