class RoutineManager:
    """
    A class to menage all routines. Its utility includes building routines,
    remembering which routines are defined and so on.
    """
    def __init__(self):
        self.list = list()

    @property
    def default(self):
        return self.list[0]

    def select(self, key=''):
        if not (type(key) is str):
            raise TypeError('Routine manager name should be a string')
        elif key is '':
            return self.default
        else:
            for routine in self.list:
                if routine.name == key:
                    return routine
        raise KeyError('No routine with name "{}" has been found'.format(key))

    def subscribe(self, new_routine):
        self.list.append(new_routine)

